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


def generer_releve_pdf(request, etudiant, classe_obj, annee, semestre=None, delib=None):
    """Génère le relevé de notes d'un étudiant en PDF avec ReportLab - format exact comme l'image"""
    
    # Importer la fonction de récupération des données depuis utils_profil_pdf
    from core.utils_profil_pdf import recuperer_donnees_profil
    
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
        elements.append(Spacer(1, 0.2*cm))
    
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
    
    title = Paragraph("<b>RELEVÉ DES NOTES</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*cm))
    
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
    
    # Infos étudiant - Tableau avec bordures invisibles (5 colonnes)
    nom_complet = getattr(etudiant, 'nom_complet', '') or f"{getattr(etudiant, 'nom_et', '')} {getattr(etudiant, 'postnom_et', '')} {getattr(etudiant, 'prenom_et', '')}"
    matricule = etudiant.matricule_et
    classe_label = getattr(classe_obj, 'code_classe', '')
    semestre_txt = f"S{semestre}" if semestre else ""
    
    # Tableau d'en-tête avec 2 lignes et 4 colonnes
    # Col1: Labels | Col2: Valeurs | Col3: Labels | Col4: Valeurs
    info_table = Table([
        # Ligne 1: Matricule | valeur | Année académique | valeur
        [Paragraph("<b>Matricule :</b>", right_style),
         Paragraph(f"{matricule}", normal_style),
         Paragraph("<b>Année académique :</b>", right_style),
         Paragraph(f"{annee}", normal_style)],
        # Ligne 2: Noms | valeur | Classe | valeur
        [Paragraph("<b>Noms :</b>", right_style),
         Paragraph(f"{nom_complet}", normal_style),
         Paragraph("<b>Classe :</b>", right_style),
         Paragraph(f"{classe_label}", normal_style)]
    ], colWidths=[2.5*cm, 4*cm, 3.5*cm, 4*cm])
    
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
    
    # Ajouter les cours depuis les données récupérées
    
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
    
    # Tableau récapitulatif - Ligne 1 (depuis les données calculées)
    moyenne_str = f"{moyenne:.1f}" if moyenne is not None else '-'
    
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
        return 'Insatisfaisant (G) : un travail considérable est nécessaire pour réussir'
    
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
    
    # Tableau récapitulatif - Ligne 2: Moyennes catégories (depuis les données calculées)
    # Utiliser les variables déjà définies (soit depuis delib, soit depuis donnees)
    moy_a_str = f"{moyenne_cat_a:.1f}" if moyenne_cat_a is not None else '-'
    moy_b_str = f"{moyenne_cat_b:.1f}" if moyenne_cat_b is not None else '-'
    
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
    elements.append(Spacer(1, 0.2*cm))
    
    # Date et lieu
    from datetime import datetime
    date_str = datetime.now().strftime("%d/%m/%Y")
    fait_a = Paragraph(f"Fait à .................................................. le {date_str}", ParagraphStyle(
        'RightStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_RIGHT,
        fontName='Helvetica',
    ))
    elements.append(fait_a)
    elements.append(Spacer(1, 0.2*cm))
    
    # Signature du chef de section (alignée à droite)
    signature_table = Table([
        [Paragraph("", normal_style), Paragraph("<b>Le Chef de Section</b>", center_style)],
        [Paragraph("", normal_style), Paragraph("<br/><br/><br/>", center_style)],  # Espace pour signature
        [Paragraph("", normal_style), Paragraph("____________________", center_style)]  # Ligne pour le nom
    ], colWidths=[12*cm, 6*cm])
    
    signature_table.setStyle(TableStyle([
        # Bordures invisibles
        ('GRID', (0, 0), (-1, -1), 0, colors.white),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),
        # Alignement
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(signature_table)
    
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    
    # Créer un nom de fichier avec le nom de l'étudiant et le type
    nom_etudiant = etudiant.nom_complet or f"{etudiant.nom_et or ''} {etudiant.postnom_et or ''} {etudiant.prenom_et or ''}".strip()
    # Nettoyer le nom pour le fichier
    nom_etudiant = nom_etudiant.replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    type_str = f"S{semestre}" if semestre else "Annuel"
    filename = f"releve_{nom_etudiant}_{type_str}_{annee}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response
