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


def recuperer_donnees_deliberation_releve(etudiant, type_deliberation, annee_academique):
    """Récupère les données simples depuis le modèle Deliberation pour le relevé"""
    from core.models import Deliberation, UE
    
    # Récupérer toutes les délibérations pour cet étudiant et ce type
    deliberations = Deliberation.objects.filter(
        matricule_etudiant=etudiant,
        type_deliberation=type_deliberation,
        annee_academique=annee_academique
    ).select_related('code_ue', 'code_ec', 'code_ec__code_ue')
    
    # Regrouper par UE pour éviter les doublons de crédits
    ue_data = {}
    
    for delib in deliberations:
        # Calculer la note finale avec la méthode du modèle
        note_finale = delib.calculer_note_finale()
        
        # Déterminer l'UE (priorité à l'UE de l'EC, sinon l'UE directe)
        if delib.code_ec and delib.code_ec.code_ue:
            ue = delib.code_ec.code_ue
            ue_code = ue.code_ue
        elif delib.code_ue:
            ue = delib.code_ue
            ue_code = ue.code_ue
        else:
            continue
        
        # Initialiser l'UE si pas encore faite
        if ue_code not in ue_data:
            ue_data[ue_code] = {
                'code_ue': ue_code,
                'intitule_ue': ue.intitule_ue,
                'categorie': getattr(ue, 'categorie', ''),
                'credit_ue': ue.credit or 0,
                'deliberations': []
            }
        
        # Ajouter la délibération à cette UE
        ue_data[ue_code]['deliberations'].append({
            'code_ec': delib.code_ec.code_ec if delib.code_ec else ue_code,
            'intitule_ec': delib.code_ec.intitule_ue if delib.code_ec else '-',
            'cc': delib.cc,
            'examen': delib.examen,
            'note': note_finale,
            'rattrapage': delib.rattrapage,
            'statut': delib.statut
        })
    
    # Préparer les lignes pour le tableau du relevé
    rows = []
    credits_total = 0
    credits_capitalises = 0
    total_points = 0
    total_credits = 0
    
    # Catégories pour les moyennes
    categories_points = {'A': 0, 'B': 0}
    categories_credits = {'A': 0, 'B': 0}
    
    for ue_code, data in ue_data.items():
        # Calculer la moyenne de l'UE (moyenne des EC)
        notes_ec = [d['note'] for d in data['deliberations'] if d['note'] is not None]
        moyenne_ue = sum(notes_ec) / len(notes_ec) if notes_ec else None
        
        # Déterminer le statut de l'UE (VALIDE seulement si TOUS les EC sont VALIDÉS)
        statut_ue = 'VALIDE' if all(d['statut'] == 'VALIDE' for d in data['deliberations']) else 'NON_VALIDE'
        
        # Calculer les crédits capitalisés de manière proportionnelle
        nb_valides = sum(1 for d in data['deliberations'] if d['statut'] == 'VALIDE')
        proportion_valide = nb_valides / len(data['deliberations'])
        credits_capitalises_ue = data['credit_ue'] * proportion_valide
        
        # Créer une ligne par EC pour l'affichage
        for i, delib_data in enumerate(data['deliberations']):
            note_finale = delib_data['note']
            
            # Notes session ordinaire et rattrapage
            note_ordinale = note_finale
            note_rattrapage = delib_data['rattrapage'] if delib_data['rattrapage'] is not None else None
            
            # Statut directement depuis le modèle Deliberation
            statut_mapping = {
                'VALIDE': 'Capitalisé',
                'NON_VALIDE': 'Non capitalisé',
                'EN_COURS': 'En cours'
            }
            statut = statut_mapping.get(delib_data['statut'], delib_data['statut'])
            
            # Créer la ligne pour le relevé
            row = {
                'code_ue': data['code_ue'],
                'intitule_ue': data['intitule_ue'],
                'credit_ue': data['credit_ue'] if i == 0 else 0,  # Crédits seulement sur première ligne
                'moyenne': moyenne_ue if i == 0 else None,  # Moyenne UE seulement sur première ligne
                'elements_constitutifs': delib_data['intitule_ec'],
                'categorie_ec': data['categorie'],
                'credit_ec': data['credit_ue'] if i == 0 else 0,  # Crédits EC seulement sur première ligne
                'note_ordinale': note_ordinale,
                'note_rattrapage': note_rattrapage,
                'statut': statut if i == 0 else ''  # Statut seulement sur première ligne
            }
            rows.append(row)
        
        # Calculer les statistiques (une seule fois par UE)
        credits_total += data['credit_ue']
        credits_capitalises += credits_capitalises_ue  # Utiliser les crédits proportionnels
        
        if moyenne_ue is not None:
            total_points += moyenne_ue * data['credit_ue']
            total_credits += data['credit_ue']
            
            # Ajouter aux catégories
            categorie = data['categorie']
            if categorie in categories_points:
                categories_points[categorie] += moyenne_ue * data['credit_ue']
                categories_credits[categorie] += data['credit_ue']
    
    # Calculer les moyennes
    moyenne = total_points / total_credits if total_credits > 0 else None
    moyenne_cat_a = categories_points['A'] / categories_credits['A'] if categories_credits['A'] > 0 else None
    moyenne_cat_b = categories_points['B'] / categories_credits['B'] if categories_credits['B'] > 0 else None
    
    # Calculer le pourcentage
    pourcentage = (credits_capitalises / credits_total * 100) if credits_total > 0 else 0
    
    # Décision du jury - basée sur les statuts du modèle Deliberation
    def _decision_jury_deliberation(credits_capitalises, credits_total, moyenne):
        if credits_capitalises >= credits_total:
            return 'Admis'
        elif credits_capitalises >= credits_total * 0.7:  # 70% ou plus = Admis avec compensation
            return 'Admis avec compensation'
        else:
            return 'Ajourné'
    
    decision = _decision_jury_deliberation(credits_capitalises, credits_total, moyenne)
    
    return {
        'rows': rows,
        'credits_total': credits_total,
        'credits_capitalises': round(credits_capitalises, 1),  # Arrondir à 1 décimale
        'credits_non_capitalises': round(credits_total - credits_capitalises, 1),
        'moyenne': moyenne,
        'moyenne_cat_a': moyenne_cat_a,
        'moyenne_cat_b': moyenne_cat_b,
        'pourcentage': round(pourcentage, 1),
        'decision': decision
    }


def generer_releve_pdf_simple(request, etudiant, classe_obj, annee, semestre, type_deliberation):
    """Génère le relevé de notes d'un étudiant en PDF avec ReportLab - utilise les données de Deliberation"""
    
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
        elements.append(Spacer(1, 0.5*cm))
    
    # Titre
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontSize=14,
        leading=16,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=10,
    )
    
    title = Paragraph("<b>RELEVÉ DE NOTES</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*cm))
    
    # Informations étudiant
    nom_complet = getattr(etudiant, 'nom_complet', '') or f"{getattr(etudiant, 'nom_et', '')} {getattr(etudiant, 'postnom_et', '')} {getattr(etudiant, 'prenom_et', '')}"
    
    info_table = Table([
        [Paragraph("<b>Nom/Postnom/prénom :</b>", right_style),
         Paragraph(f"{nom_complet}", normal_style),
         Paragraph("<b>Matricule :</b>", right_style),
         Paragraph(f"{etudiant.matricule_et}", normal_style)],
        [Paragraph("<b>Sexe :</b>", right_style),
         Paragraph(f"{etudiant.sexe}", normal_style),
         Paragraph("<b>Lieu et date de naissance :</b>", right_style),
         Paragraph(f"{getattr(etudiant, 'lieu_naiss', '')}, {getattr(etudiant, 'date_naiss', '')}", normal_style)]
    ], colWidths=[4*cm, 6*cm, 4*cm, 6*cm])
    
    info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0, colors.white),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 4*mm))
    
    # Récupérer les données de délibération
    donnees = recuperer_donnees_deliberation_releve(etudiant, type_deliberation, annee)
    rows = donnees.get('rows', [])
    credits_total = donnees.get('credits_total', 0)
    credits_capitalises = donnees.get('credits_capitalises', 0)
    credits_non_capitalises = donnees.get('credits_non_capitalises', 0)
    moyenne = donnees.get('moyenne')
    moyenne_cat_a = donnees.get('moyenne_cat_a')
    moyenne_cat_b = donnees.get('moyenne_cat_b')
    pourcentage = donnees.get('pourcentage', 0)
    decision = donnees.get('decision')
    
    # Tableau des cours
    table_data = [[
        Paragraph('<b>Code UE</b>', table_header_style),
        Paragraph('<b>Unité d\'Enseignement</b>', table_header_style),
        Paragraph('<b>Cr</b>', table_header_style),
        Paragraph('<b>Moy</b>', table_header_style),
        Paragraph('<b>Éléments Constitutifs</b>', table_header_style),
        Paragraph('<b>Catégorie</b>', table_header_style),
        Paragraph('<b>Cr</b>', table_header_style),
        Paragraph('<b>Note session ordinaire</b>', table_header_style),
        Paragraph('<b>Note session rattrapage</b>', table_header_style),
        Paragraph('<b>ETAT</b>', table_header_style)
    ]]
    
    for row in rows:
        moy_str = f"{row['moyenne']:.1f}" if row['moyenne'] is not None else '-'
        note_ord_str = f"{row['note_ordinale']:.1f}" if row['note_ordinale'] is not None else '-'
        note_ratt_str = f"{row['note_rattrapage']:.1f}" if row['note_rattrapage'] is not None else '-'
        
        table_data.append([
            Paragraph(row['code_ue'], table_cell_style),
            Paragraph(row['intitule_ue'], table_cell_style),
            Paragraph(str(row['credit_ue']), table_cell_center),
            Paragraph(moy_str, table_cell_center),
            Paragraph(row['elements_constitutifs'], table_cell_style),
            Paragraph(row['categorie_ec'], table_cell_center),
            Paragraph(str(row['credit_ec']), table_cell_center),
            Paragraph(note_ord_str, table_cell_center),
            Paragraph(note_ratt_str, table_cell_center),
            Paragraph(row['statut'], table_cell_center)
        ])
    
    col_widths = [1.5*cm, 4*cm, 0.8*cm, 0.8*cm, 3.5*cm, 1.2*cm, 0.8*cm, 2*cm, 2*cm, 1.5*cm]
    
    cours_table = Table(table_data, colWidths=col_widths)
    cours_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    
    elements.append(cours_table)
    elements.append(Spacer(1, 4*mm))
    
    # Lignes de synthèse
    def _format_decimal(value):
        if value is None:
            return '-'
        return f"{value:.1f}"
    
    # Ligne synthèse 1: Moyennes catégories
    moy_a_str = _format_decimal(moyenne_cat_a)
    moy_b_str = _format_decimal(moyenne_cat_b)
    
    synthese1 = Table([
        [Paragraph('<b>MOYENNE DE LA CATEGORIE A</b>', table_cell_style),
         Paragraph(moy_a_str, table_cell_center),
         Paragraph('<b>MOYENNE DE LA CATEGORIE B</b>', table_cell_style),
         Paragraph(moy_b_str, table_cell_center)]
    ], colWidths=[4*cm, 3*cm, 4*cm, 3*cm])
    synthese1.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(synthese1)
    elements.append(Spacer(1, 2*mm))
    
    # Ligne synthèse 2: Moyenne générale et pourcentage
    moyenne_str = _format_decimal(moyenne)
    pourcentage_str = f"{pourcentage:.1f}%"
    
    synthese2 = Table([
        [Paragraph('<b>MOYENNE</b>', table_cell_style),
         Paragraph(moyenne_str, table_cell_center),
         Paragraph('<b>POURCENTAGE</b>', table_cell_style),
         Paragraph(pourcentage_str, table_cell_center)]
    ], colWidths=[4*cm, 3*cm, 4*cm, 3*cm])
    synthese2.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(synthese2)
    elements.append(Spacer(1, 2*mm))
    
    # Ligne synthèse 3: Crédits et décision
    synthese3 = Table([
        [Paragraph('<b>Nombre des crédits capitalisés</b>', table_cell_style),
         Paragraph(str(credits_capitalises), table_cell_center),
         Paragraph('<b>Nombre des crédits non capitalisés</b>', table_cell_style),
         Paragraph(str(credits_non_capitalises), table_cell_center)]
    ], colWidths=[4*cm, 3*cm, 4*cm, 3*cm])
    synthese3.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(synthese3)
    elements.append(Spacer(1, 2*mm))
    
    # Ligne synthèse 4: Décision du jury
    synthese4 = Table([
        [Paragraph('<b>Décision du jury</b>', table_cell_style),
         Paragraph(decision, table_cell_center)]
    ], colWidths=[8*cm, 6*cm])
    synthese4.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(synthese4)
    elements.append(Spacer(1, 0.8*cm))
    
    # Date et lieu
    from datetime import datetime
    date_str = datetime.now().strftime("%d/%m/%Y")
    fait_a = Paragraph(f"Fait à .................................................. le {date_str}", right_style)
    elements.append(fait_a)
    
    # Construire le PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="releve_{etudiant.matricule_et}_{type_deliberation}.pdf"'
    return response
