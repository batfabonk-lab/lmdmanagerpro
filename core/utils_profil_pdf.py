from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings
import os
from django.db.models import Sum, Avg, Case, When, F, FloatField, Value
from django.db.models.functions import Round


def recuperer_donnees_profil(etudiant, classe_obj, annee, semestre):
    """Récupère les données du profil avec les jointures SQL comme dans la requête fournie"""
    from core.models import Evaluation, EC, UE
    
    def _apply_compensation_1_to_1(fails, donors):
        """Applique la compensation 1 à 1 entre EC/UE en échec (8-9) et donateurs (>10)"""
        fail_items = []
        for key, note in fails:
            deficit = 10 - float(note)
            fail_items.append((key, float(note), deficit))

        donor_items = []
        for key, note in donors:
            excess = float(note) - 10
            donor_items.append((key, float(note), excess))

        fail_items.sort(key=lambda x: x[2], reverse=True)
        donor_items.sort(key=lambda x: x[2])

        compensated = set()
        used_donors = set()
        for f_key, f_note, deficit in fail_items:
            for d_key, d_note, excess in donor_items:
                if d_key in used_donors:
                    continue
                if excess >= deficit:
                    used_donors.add(d_key)
                    compensated.add(f_key)
                    break
        return compensated
    
    # Récupérer toutes les évaluations (UE directes et EC)
    evaluations = Evaluation.objects.filter(
        matricule_etudiant=etudiant,
        statut__in=['VALIDE', 'NON_VALIDE']
    ).select_related(
        'code_ue',
        'code_ec',
        'code_ec__code_ue'
    )
    
    # Filtrer par semestre si nécessaire
    if semestre:
        from django.db.models import Q
        evaluations = evaluations.filter(
            Q(code_ec__code_ue__semestre=semestre) | Q(code_ue__semestre=semestre)
        )
    
    # Construire un tableau structuré des données par UE
    ue_tableau = {}  # Tableau pour regrouper les évaluations par UE
    ec_compensated_ids = set()  # EC compensés
    
    for ev in evaluations:
        # Cas 1: Évaluation d'un EC (qui appartient à une UE)
        if ev.code_ec and ev.code_ec.code_ue:
            ec = ev.code_ec
            ue = ec.code_ue
            
            # Initialiser l'UE dans le tableau si nécessaire
            if ue.code_ue not in ue_tableau:
                ue_tableau[ue.code_ue] = {
                    'ue': ue,
                    'code_ue': ue.code_ue,
                    'intitule_ue': ue.intitule_ue,
                    'categorie': ue.categorie,
                    'credit_ue': ue.credit,
                    'ec_list': [],
                    'evaluations': []
                }
            
            # Calculer les valeurs
            cc = ev.cc if ev.cc is not None else None
            examen = ev.examen if ev.examen is not None else None
            note = (cc + examen) if (cc is not None and examen is not None) else None
            credit_affiche = ec.credit
            note_ponderee = (note * credit_affiche) if note is not None else None
            rattrapage = ev.rattrapage if ev.rattrapage is not None else None
            statut = 'Validé' if note is not None and note >= 10 else 'Non validé'
            
            # Ajouter l'EC à la liste des EC de cette UE
            ue_tableau[ue.code_ue]['ec_list'].append({
                'code_ec': ec.code_ec,
                'intitule_ec': ec.intitule_ue,
                'credit': credit_affiche,
                'cc': cc,
                'examen': examen,
                'note': note,
                'note_ponderee': note_ponderee,
                'rattrapage': rattrapage,
                'statut': statut
            })
            ue_tableau[ue.code_ue]['evaluations'].append(ev)
        
        # Cas 2: Évaluation directe d'une UE (sans EC)
        elif ev.code_ue and not ev.code_ec:
            ue = ev.code_ue
            
            # Initialiser l'UE dans le tableau si nécessaire
            if ue.code_ue not in ue_tableau:
                ue_tableau[ue.code_ue] = {
                    'ue': ue,
                    'code_ue': ue.code_ue,
                    'intitule_ue': ue.intitule_ue,
                    'categorie': ue.categorie,
                    'credit_ue': ue.credit,
                    'ec_list': [],
                    'evaluations': []
                }
            
            # Calculer les valeurs
            cc = ev.cc if ev.cc is not None else None
            examen = ev.examen if ev.examen is not None else None
            note = (cc + examen) if (cc is not None and examen is not None) else None
            credit_affiche = ue.credit
            note_ponderee = (note * credit_affiche) if note is not None else None
            rattrapage = ev.rattrapage if ev.rattrapage is not None else None
            statut = 'Validé' if note is not None and note >= 10 else 'Non validé'
            
            # Ajouter l'UE directe (sans EC)
            ue_tableau[ue.code_ue]['ec_list'].append({
                'code_ec': ue.code_ue,  # Code UE
                'intitule_ec': '-',  # Pas d'EC
                'credit': credit_affiche,
                'cc': cc,
                'examen': examen,
                'note': note,
                'note_ponderee': note_ponderee,
                'rattrapage': rattrapage,
                'statut': statut
            })
            ue_tableau[ue.code_ue]['evaluations'].append(ev)
    
    # Trier le tableau par code UE et construire les lignes finales
    rows = []
    ue_dict = {}  # Pour les calculs de statistiques
    ue_compensated_ids = set()  # UE compensées
    
    for code_ue in sorted(ue_tableau.keys()):
        ue_data = ue_tableau[code_ue]
        ue_dict[code_ue] = {
            'ue': ue_data['ue'],
            'evaluations': ue_data['evaluations']
        }
        
        # Trier les EC par code
        ec_list_sorted = sorted(ue_data['ec_list'], key=lambda x: x['code_ec'])
        
        # Créer une ligne pour chaque EC (statut sera mis à jour après calcul des moyennes)
        for ec_data in ec_list_sorted:
            note = ec_data['note']
            code_ec = ec_data['code_ec']
            
            # Statut temporaire (sera mis à jour après compensation)
            if note is not None:
                if note >= 10:
                    statut = 'Validé'
                else:
                    statut = 'Non validé'
            else:
                statut = 'Non validé'
            
            row = {
                'code_ue': ue_data['code_ue'],
                'code_ec': code_ec,
                'intitule_ue': ue_data['intitule_ue'],
                'intitule_ec': ec_data['intitule_ec'],
                'categorie': ue_data['categorie'],
                'credit': ec_data['credit'],
                'cc': ec_data['cc'],
                'examen': ec_data['examen'],
                'note': note,
                'note_ponderee': ec_data['note_ponderee'],
                'rattrapage': ec_data['rattrapage'],
                'statut': statut,
                'compensated': False
            }
            rows.append(row)
    
    # Calculer les statistiques récapitulatives
    # Nombre total de crédits (somme des crédits des EC/UE)
    credits_total = 0
    for row in rows:
        credits_total += row['credit']
    
    # Nombre de crédits capitalisés (note >= 10 OU compensé pour chaque EC/UE)
    credits_valides = 0
    for row in rows:
        if row['note'] is not None and (row['note'] >= 10 or row.get('compensated', False)):
            credits_valides += row['credit']
    
    # Calculer les moyennes pondérées par les crédits
    # Moyenne générale = somme(note * crédit) / somme(crédits)
    total_notes_ponderees = 0
    total_credits_notes = 0
    
    # Moyenne catégorie A
    total_notes_ponderees_a = 0
    total_credits_a = 0
    
    # Moyenne catégorie B
    total_notes_ponderees_b = 0
    total_credits_b = 0
    
    for row in rows:
        note = row['note']
        credit = row['credit']
        categorie = row['categorie']
        
        if note is not None:
            note_ponderee = note * credit
            total_notes_ponderees += note_ponderee
            total_credits_notes += credit
            
            # Ajouter aux moyennes par catégorie
            if categorie == 'A':
                total_notes_ponderees_a += note_ponderee
                total_credits_a += credit
            elif categorie == 'B':
                total_notes_ponderees_b += note_ponderee
                total_credits_b += credit
    
    # Calculer les moyennes
    moyenne = round(total_notes_ponderees / total_credits_notes, 2) if total_credits_notes > 0 else None
    moyenne_cat_a = round(total_notes_ponderees_a / total_credits_a, 2) if total_credits_a > 0 else None
    moyenne_cat_b = round(total_notes_ponderees_b / total_credits_b, 2) if total_credits_b > 0 else None
    
    # Appliquer la compensation des EC au sein de chaque UE (si moyenne catégorie >= 10)
    for code_ue, ue_data in ue_tableau.items():
        ue = ue_data['ue']
        categorie = ue.categorie
        
        # Vérifier si la moyenne de la catégorie est >= 10
        moyenne_cat = moyenne_cat_a if categorie == 'A' else moyenne_cat_b
        if moyenne_cat is None or moyenne_cat < 10:
            continue
        
        fails = []
        donors = []
        
        for ec_data in ue_data['ec_list']:
            note = ec_data['note']
            if note is not None:
                # Règle stricte : note < 8 ne peut jamais être compensée
                if 8 <= note < 10:
                    fails.append((ec_data['code_ec'], note))
                elif note > 10:
                    donors.append((ec_data['code_ec'], note))
        
        # Appliquer la compensation 1 à 1
        compensated_ec = _apply_compensation_1_to_1(fails, donors)
        ec_compensated_ids |= compensated_ec
    
    # Appliquer la compensation des UE par catégorie (si moyenne catégorie >= 10)
    # Calculer les notes moyennes par UE pour la compensation
    ue_notes = {}
    for code_ue, data in ue_dict.items():
        ue = data['ue']
        evals = data['evaluations']
        
        notes_ue = []
        for ev in evals:
            if ev.cc is not None and ev.examen is not None:
                note = ev.cc + ev.examen
                notes_ue.append(note)
        
        if notes_ue:
            ue_notes[code_ue] = sum(notes_ue) / len(notes_ue)
    
    # Compensation par catégorie
    for cat, moyenne_cat in [('A', moyenne_cat_a), ('B', moyenne_cat_b)]:
        if moyenne_cat is None or moyenne_cat < 10:
            continue
        
        fails_ue = []
        donors_ue = []
        
        for code_ue, note_ue in ue_notes.items():
            ue = ue_dict[code_ue]['ue']
            if ue.categorie != cat:
                continue
            
            # Règle stricte : note UE < 8 ne peut jamais être compensée
            if 8 <= note_ue < 10:
                fails_ue.append((code_ue, note_ue))
            elif note_ue > 10:
                donors_ue.append((code_ue, note_ue))
        
        # Appliquer la compensation 1 à 1 au niveau UE
        compensated_ue = _apply_compensation_1_to_1(fails_ue, donors_ue)
        ue_compensated_ids |= compensated_ue
    
    # Mettre à jour les statuts des lignes avec la compensation
    for row in rows:
        code_ue = row['code_ue']
        code_ec = row['code_ec']
        note = row['note']
        
        if note is not None:
            if note >= 10:
                row['statut'] = 'Validé'
                row['compensated'] = False
            elif note < 8:
                # Règle stricte : note < 8 ne peut JAMAIS être validée
                row['statut'] = 'Non validé'
                row['compensated'] = False
            elif code_ue in ue_compensated_ids:
                row['statut'] = 'Validé'
                row['compensated'] = True
            elif code_ec in ec_compensated_ids:
                row['statut'] = 'Validé'
                row['compensated'] = True
            else:
                row['statut'] = 'Non validé'
                row['compensated'] = False
        else:
            row['statut'] = 'Non validé'
            row['compensated'] = False
    
    # Recalculer les crédits capitalisés en tenant compte de la compensation
    # Validé si: note >= 10 OU (EC compensé ET note >= 8)
    # Règle stricte : note < 8 ne compte JAMAIS dans les crédits capitalisés
    credits_valides = 0
    for row in rows:
        note = row['note']
        
        if note is not None:
            if note >= 10:
                credits_valides += row['credit']
            elif note >= 8 and row.get('compensated', False):
                credits_valides += row['credit']
    
    return {
        'rows': rows,
        'credits_total': credits_total,
        'credits_valides': credits_valides,
        'moyenne': moyenne,
        'moyenne_cat_a': moyenne_cat_a,
        'moyenne_cat_b': moyenne_cat_b,
        'ec_compensated_ids': list(ec_compensated_ids),
        'ue_compensated_ids': list(ue_compensated_ids)
    }


def generer_profil_pdf(request, etudiant, classe_obj, annee, semestre, delib):
    """Génère le profil de l'étudiant en PDF avec ReportLab - format exact comme l'image"""
    
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.2*cm,
        leftMargin=1.2*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Styles
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.black,
        alignment=TA_LEFT,
        fontName='Helvetica',
    )
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.black,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
    )
    
    center_style = ParagraphStyle(
        'CenterStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica',
    )
    
    right_style = ParagraphStyle(
        'RightStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.black,
        alignment=TA_RIGHT,
        fontName='Helvetica',
    )
    
    table_header_style = ParagraphStyle(
        'TableHeaderStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=9,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )
    
    table_cell_style = ParagraphStyle(
        'TableCellStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=9,
        textColor=colors.black,
        alignment=TA_LEFT,
        fontName='Helvetica',
    )
    
    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontSize=8,
        leading=9,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica',
    )
    
    # En-tête avec image PNG
    entete_path = os.path.join(settings.MEDIA_ROOT, 'entete.png')
    if os.path.exists(entete_path):
        from PIL import Image as PILImage
        pil_img = PILImage.open(entete_path)
        img_width, img_height = pil_img.size
        ratio = img_height / img_width
        desired_width = 18*cm
        desired_height = desired_width * ratio
        img = RLImage(entete_path, width=desired_width, height=desired_height)
        elements.append(img)
        elements.append(Spacer(1, 0.5*cm))
    
    # Largeur totale disponible
    page_width = 18*cm
    
    # Titre avec police Algerian
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontSize=14,
        leading=16,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',  # Fallback si Algerian n'est pas disponible
        spaceAfter=10,
    )
    
    # Essayer d'utiliser la police Algerian si disponible
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        # Tenter d'enregistrer Algerian (si disponible sur le système)
        # Sinon, utiliser Helvetica-Bold comme fallback
        title_style.fontName = 'Helvetica-Bold'
    except:
        title_style.fontName = 'Helvetica-Bold'
    
    title = Paragraph("<b>PROFIL DE L'ÉTUDIANT</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*cm))
    
    # Infos étudiant - Tableau avec bordures invisibles
    nom_complet = getattr(etudiant, 'nom_complet', '') or f"{getattr(etudiant, 'nom_et', '')} {getattr(etudiant, 'postnom_et', '')} {getattr(etudiant, 'prenom_et', '')}"
    classe_label = getattr(classe_obj, 'code_classe', '')
    semestre_txt = f"S{semestre}" if semestre else ""
    
    # Tableau d'en-tête avec 2 lignes et 5 colonnes
    # Col1: Labels | Col2: Valeurs | Col3: Labels | Col4: Valeurs | Col5: Semestre/Annuel
    # Déterminer le texte pour la dernière colonne
    periode_txt = f"S{semestre}" if semestre else "Annuel"
    info_table = Table([
        # Ligne 1: Matricule | valeur | Année académique | valeur | Semestre/Annuel
        [Paragraph("<b>Matricule :</b>", right_style),
         Paragraph(f"{etudiant.matricule_et}", normal_style),
         Paragraph("<b>Année académique :</b>", right_style),
         Paragraph(f"{annee}", normal_style),
         Paragraph(f"<b>Période :</b> {periode_txt}", normal_style)],
        # Ligne 2: Noms | valeur | Classe | valeur | (vide)
        [Paragraph("<b>Noms :</b>", right_style),
         Paragraph(f"{nom_complet}", normal_style),
         Paragraph("<b>Classe :</b>", right_style),
         Paragraph(f"{classe_label}", normal_style),
         Paragraph("", normal_style)]
    ], colWidths=[2.5*cm, 4*cm, 3.5*cm, 4*cm, 4*cm])
    
    info_table.setStyle(TableStyle([
        # Pas de bordures (invisibles)
        ('GRID', (0, 0), (-1, -1), 0, colors.white),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),
        # Alignement vertical
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 4*mm))
    
    # Tableau des notes - 11 colonnes exactement comme l'image
    # Code | Intitulé de l'UE | Éléments constitutifs | Cat. | Cr | CC | Exam | Note | N.Pd | Ratt | Statut
    table_data = [[
        Paragraph('<b>Code</b>', table_header_style),
        Paragraph('<b>Intitulé de l\'UE</b>', table_header_style),
        Paragraph('<b>Éléments constitutifs</b>', table_header_style),
        Paragraph('<b>Cat.</b>', table_header_style),
        Paragraph('<b>Cr</b>', table_header_style),
        Paragraph('<b>CC</b>', table_header_style),
        Paragraph('<b>Exam</b>', table_header_style),
        Paragraph('<b>Note</b>', table_header_style),
        Paragraph('<b>N.Pd</b>', table_header_style),
        Paragraph('<b>Ratt</b>', table_header_style),
        Paragraph('<b>Statut</b>', table_header_style)
    ]]
    
    # Récupérer les données - utiliser directement les données de délibération
    if delib and 'rows' in delib:
        # Utiliser directement les données de délibération (depuis _jury_compute_delib_ues)
        rows = delib.get('rows', [])
        credits_total = delib.get('credits_total', 0)
        credits_valides = delib.get('credits_valides', 0)
        moyenne = delib.get('moyenne')
        moyenne_cat_a = delib.get('moyenne_cat_a')
        moyenne_cat_b = delib.get('moyenne_cat_b')
        decision_label_calc = delib.get('decision_label')
        decision_code_calc = delib.get('decision_code')
    else:
        # Fallback: utiliser les données standard (semestrielles)
        donnees = recuperer_donnees_profil(etudiant, classe_obj, annee, semestre)
        rows = donnees.get('rows', [])
        credits_total = donnees.get('credits_total', 0)
        credits_valides = donnees.get('credits_valides', 0)
        moyenne = donnees.get('moyenne')
        moyenne_cat_a = donnees.get('moyenne_cat_a')
        moyenne_cat_b = donnees.get('moyenne_cat_b')
        decision_label_calc = None
        decision_code_calc = None
    
    for row in rows:
        code_ec = str(row.get('code_ec', ''))
        intitule_ue = str(row.get('intitule_ue', ''))
        intitule_ec = str(row.get('intitule_ec', ''))
        categorie = str(row.get('categorie', '') or '')
        credit = str(row.get('credit', '') or '')
        
        cc_val = row.get('cc')
        exa_val = row.get('examen')
        note_val = row.get('note')
        note_pd_val = row.get('note_ponderee')
        ratt_val = row.get('rattrapage')
        statut = str(row.get('statut', '') or '')
        
        cc_str = f"{cc_val:.1f}" if cc_val is not None else '-'
        exa_str = f"{exa_val:.1f}" if exa_val is not None else '-'
        note_str = f"{note_val:.1f}" if note_val is not None else '-'
        note_pd_str = f"{note_pd_val:.1f}" if note_pd_val is not None else '-'
        ratt_str = f"{ratt_val:.1f}" if ratt_val is not None else '-'
        
        table_data.append([
            Paragraph(code_ec, table_cell_style),
            Paragraph(intitule_ue, table_cell_style),
            Paragraph(intitule_ec, table_cell_style),
            Paragraph(categorie, table_cell_center),
            Paragraph(credit, table_cell_center),
            Paragraph(cc_str, table_cell_center),
            Paragraph(exa_str, table_cell_center),
            Paragraph(note_str, table_cell_center),
            Paragraph(note_pd_str, table_cell_center),
            Paragraph(ratt_str, table_cell_center),
            Paragraph(statut, table_cell_center)
        ])
    
    # Largeurs colonnes - proportions exactes comme l'image (+2cm de largeur totale)
    # Code: 1.5cm, Intitulé UE: 3.8cm, Éléments: 5.2cm, Cat: 0.9cm, Cr: 0.8cm, CC: 0.9cm, Exam: 1.0cm, Note: 0.9cm, N.Pd: 1.0cm, Ratt: 0.9cm, Statut: 1.8cm
    col_widths = [1.5*cm, 3.8*cm, 5.2*cm, 0.9*cm, 0.8*cm, 0.9*cm, 1.0*cm, 0.9*cm, 1.0*cm, 0.9*cm, 1.8*cm]
    
    cours_table = Table(table_data, colWidths=col_widths)
    cours_table.setStyle(TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Corps
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (2, -1), 'LEFT'),
        ('ALIGN', (3, 1), (-1, -1), 'CENTER'),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        
        # Grille
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    
    elements.append(cours_table)
    elements.append(Spacer(1, 4*mm))
    
    # Tableau récapitulatif - Ligne 1
    # Utiliser les données calculées (délibération ou standard)
    def _format_decimal(value):
        """Formater un nombre avec un chiffre après la virgule sans arrondir"""
        if value is None:
            return '-'
        # Convertir en chaîne et garder un chiffre après la virgule
        str_value = str(value)
        if '.' in str_value:
            parts = str_value.split('.')
            if len(parts[1]) > 1:
                return f"{parts[0]}.{parts[1][0]}"
            else:
                return str_value
        else:
            return f"{str_value}.0"
    
    moyenne_str = _format_decimal(moyenne)
    
    # Calculer la décision avec la même logique que le palmarès
    def _mention_for_note(note):
        if note is None:
            return 'A déterminer'
        n = float(note)
        if n >= 18:
            return 'Excellent (A)'
        if n >= 16:
            return 'Très bien (B)'
        if n >= 14:
            return 'Bien (C)'
        if n >= 12:
            return 'Assez Bien (D)'
        if n >= 10:
            return 'Passable (E)'
        if n >= 8:
            return 'Insuffisant (F)'
        return 'Insatisfaisant (G)'
    
    def _decision_for_credits(credits_valides, credits_total, semestre=None):
        """Détermine la décision du jury selon les crédits capitalisés pour un profil semestriel ou annuel"""
        if credits_valides is None:
            return 'A déterminer'
        
        # Adapter les seuils selon le type de profil
        if semestre is None:  # Profil annuel
            if credits_valides >= 60:
                return 'Année validée'
            elif credits_valides >= 45:
                return 'Compensable'
            else:
                return 'Ajourné'
        else:  # Profil semestriel
            if credits_valides >= 30:
                return 'Semestre validé'
            elif credits_valides >= 15:
                return 'Compensable'
            else:
                return 'Ajourné'
    
    decision = _mention_for_note(moyenne)
    if decision_label_calc and decision_code_calc:
        if decision_code_calc == 'DEF':
            decision_jury = 'Défaillant (DEF)'
        else:
            decision_jury = f"{decision_label_calc} ({decision_code_calc})"
    else:
        decision_jury = _decision_for_credits(credits_valides, credits_total, semestre)
    
    summary1 = Table([
        [Paragraph('<b>Total crédits</b>', table_cell_style),
         Paragraph(str(credits_total), table_cell_center),
         Paragraph('<b>Crédits capitalisés</b>', table_cell_style),
         Paragraph(str(credits_valides), table_cell_center),
         Paragraph('<b>Moyenne</b>', table_cell_style),
         Paragraph(moyenne_str, table_cell_center),
         Paragraph('<b>Mention</b>', table_cell_style),
         Paragraph(decision, table_cell_center)]
    ], colWidths=[3*cm, 1.2*cm, 3.8*cm, 1.2*cm, 2*cm, 1.2*cm, 2*cm, 3.6*cm])
    summary1.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(summary1)
    elements.append(Spacer(1, 2*mm))
    
    # Tableau récapitulatif - Ligne 2: Moyennes catégories
    # Utiliser les variables déjà définies (soit depuis delib, soit depuis donnees)
    moy_a_str = _format_decimal(moyenne_cat_a)
    moy_b_str = _format_decimal(moyenne_cat_b)
    
    summary2 = Table([
        [Paragraph('<b>Catégorie A</b>', table_cell_style),
         Paragraph(moy_a_str, table_cell_center),
         Paragraph('<b>Catégorie B</b>', table_cell_style),
         Paragraph(moy_b_str, table_cell_center),
         Paragraph('<b>Décision du jury</b>', table_cell_style),
         Paragraph(decision_jury, table_cell_center)]
    ], colWidths=[3.5*cm, 3*cm, 3.5*cm, 3*cm, 3.5*cm, 2.5*cm])
    summary2.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(summary2)
    elements.append(Spacer(1, 0.8*cm))
    
    # Date et lieu
    from datetime import datetime
    date_str = datetime.now().strftime("%d/%m/%Y")
    fait_a = Paragraph(f"Fait à .................................................. le {date_str}", right_style)
    elements.append(fait_a)
    elements.append(Spacer(1, 0.6*cm))
    
    # Récupérer les membres du jury de la classe
    from core.models import Jury, Enseignant
    try:
        jury = Jury.objects.filter(code_classe=classe_obj).first()
        if jury:
            # Récupérer les informations depuis la table Enseignant en utilisant les matricules
            # Le champ membre/president/secretaire contient le matricule de l'enseignant
            
            # Membre du jury
            if jury.membre:
                try:
                    enseignant_membre = Enseignant.objects.get(matricule_en=jury.membre)
                    membre_nom = enseignant_membre.nom_complet
                    membre_grade = enseignant_membre.grade.designation_grade if enseignant_membre.grade else "Grade: _______________"
                except:
                    membre_nom = jury.membre
                    membre_grade = "Grade: _______________"
            else:
                membre_nom = "____________________"
                membre_grade = "Grade: _______________"
            
            # Président du jury
            if jury.president:
                try:
                    enseignant_president = Enseignant.objects.get(matricule_en=jury.president)
                    president_nom = enseignant_president.nom_complet
                    president_grade = enseignant_president.grade.designation_grade if enseignant_president.grade else "Grade: _______________"
                except:
                    president_nom = jury.president
                    president_grade = "Grade: _______________"
            else:
                president_nom = "____________________"
                president_grade = "Grade: _______________"
            
            # Secrétaire du jury
            if jury.secretaire:
                try:
                    enseignant_secretaire = Enseignant.objects.get(matricule_en=jury.secretaire)
                    secretaire_nom = enseignant_secretaire.nom_complet
                    secretaire_grade = enseignant_secretaire.grade.designation_grade if enseignant_secretaire.grade else "Grade: _______________"
                except:
                    secretaire_nom = jury.secretaire
                    secretaire_grade = "Grade: _______________"
            else:
                secretaire_nom = "____________________"
                secretaire_grade = "Grade: _______________"
        else:
            membre_nom = "____________________"
            membre_grade = "Grade: _______________"
            president_nom = "____________________"
            president_grade = "Grade: _______________"
            secretaire_nom = "____________________"
            secretaire_grade = "Grade: _______________"
    except Exception as e:
        membre_nom = "____________________"
        membre_grade = "Grade: _______________"
        president_nom = "____________________"
        president_grade = "Grade: _______________"
        secretaire_nom = "____________________"
        secretaire_grade = "Grade: _______________"
    
    # Style pour les noms soulignés
    underline_style = ParagraphStyle(
        'UnderlineStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        fontName='Helvetica',
    )
    
    # Style pour le grade en italique
    italic_style = ParagraphStyle(
        'ItalicStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
    )
    
    # Section des signataires (3 colonnes) avec les noms soulignés et grades en italique
    signataires_table = Table([
        # Ligne 1: Titres
        [Paragraph("<b>Membre du jury</b>", center_style),
         Paragraph("<b>Président du jury</b>", center_style),
         Paragraph("<b>Secrétaire du jury</b>", center_style)],
        # Ligne 2: Espace pour signature (réduit)
        [Paragraph("<br/><br/>", center_style),
         Paragraph("<br/><br/>", center_style),
         Paragraph("<br/><br/>", center_style)],
        # Ligne 3: Noms des membres du jury (soulignés)
        [Paragraph(f"<u>{membre_nom}</u>", underline_style),
         Paragraph(f"<u>{president_nom}</u>", underline_style),
         Paragraph(f"<u>{secretaire_nom}</u>", underline_style)],
        # Ligne 4: Grades en italique (récupérés depuis la BD)
        [Paragraph(f"<i>{membre_grade}</i>", italic_style),
         Paragraph(f"<i>{president_grade}</i>", italic_style),
         Paragraph(f"<i>{secretaire_grade}</i>", italic_style)]
    ], colWidths=[6*cm, 6*cm, 6*cm])
    
    signataires_table.setStyle(TableStyle([
        # Bordures invisibles
        ('GRID', (0, 0), (-1, -1), 0, colors.white),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),
        # Alignement
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        # Padding réduit entre les lignes
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    
    elements.append(signataires_table)
    
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    
    # Créer un nom de fichier avec le nom de l'étudiant et le type
    nom_etudiant = etudiant.nom_complet or f"{etudiant.nom_et or ''} {etudiant.postnom_et or ''} {etudiant.prenom_et or ''}".strip()
    # Nettoyer le nom pour le fichier
    nom_etudiant = nom_etudiant.replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    type_str = f"S{semestre}" if semestre else "Annuel"
    filename = f"profil_{nom_etudiant}_{type_str}_{annee}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response
