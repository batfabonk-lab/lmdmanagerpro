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


def recuperer_donnees_deliberation(etudiant, type_deliberation, annee_academique):
    """Récupère les données simples depuis le modèle Deliberation sans calculs complexes"""
    # Retourner des données vides tout en gardant la structure
    return {
        'rows': [],  # Tableau vide
        'credits_total': 0,
        'credits_valides': 0,
        'moyenne': None,
        'moyenne_cat_a': None,
        'moyenne_cat_b': None
    }


def generer_profil_pdf_simple(request, etudiant, classe_obj, annee, semestre, type_deliberation):
    """Génère le profil de l'étudiant en PDF avec ReportLab - utilise les données de Deliberation"""
    
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
    from lmdmanagersystem.middleware import get_entete_path
    entete_path = get_entete_path()
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
    
    title = Paragraph("<b>PROFIL DE L'ÉTUDIANT</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*cm))
    
    # Infos étudiant
    nom_complet = getattr(etudiant, 'nom_complet', '') or f"{getattr(etudiant, 'nom_et', '')} {getattr(etudiant, 'postnom_et', '')} {getattr(etudiant, 'prenom_et', '')}"
    classe_label = getattr(classe_obj, 'code_classe', '')
    periode_txt = type_deliberation if type_deliberation else f"S{semestre}" if semestre else "Annuel"
    
    info_table = Table([
        [Paragraph("<b>Matricule :</b>", right_style),
         Paragraph(f"{etudiant.matricule_et}", normal_style),
         Paragraph("<b>Année académique :</b>", right_style),
         Paragraph(f"{annee}", normal_style),
         Paragraph(f"<b>Période :</b> {periode_txt}", normal_style)],
        [Paragraph("<b>Noms :</b>", right_style),
         Paragraph(f"{nom_complet}", normal_style),
         Paragraph("<b>Classe :</b>", right_style),
         Paragraph(f"{classe_label}", normal_style),
         Paragraph("", normal_style)]
    ], colWidths=[2.5*cm, 4*cm, 3.5*cm, 4*cm, 4*cm])
    
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
    donnees = recuperer_donnees_deliberation(etudiant, type_deliberation, annee)
    rows = donnees.get('rows', [])
    credits_total = donnees.get('credits_total', 0)
    credits_valides = donnees.get('credits_valides', 0)
    moyenne = donnees.get('moyenne')
    moyenne_cat_a = donnees.get('moyenne_cat_a')
    moyenne_cat_b = donnees.get('moyenne_cat_b')
    
    # Tableau des notes
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
    
    # Si aucune donnée, ajouter une ligne vide pour la structure
    if not rows:
        table_data.append([
            Paragraph('-', table_cell_center),
            Paragraph('-', table_cell_center),
            Paragraph('-', table_cell_center),
            Paragraph('-', table_cell_center),
            Paragraph('-', table_cell_center),
            Paragraph('-', table_cell_center),
            Paragraph('-', table_cell_center),
            Paragraph('-', table_cell_center),
            Paragraph('-', table_cell_center),
            Paragraph('-', table_cell_center),
            Paragraph('-', table_cell_center)
        ])
    else:
        for row in rows:
            cc_str = f"{row['cc']:.1f}" if row['cc'] is not None else '-'
            exa_str = f"{row['examen']:.1f}" if row['examen'] is not None else '-'
            note_str = f"{row['note']:.1f}" if row['note'] is not None else '-'
            note_pd_str = f"{row['note_ponderee']:.1f}" if row['note_ponderee'] is not None else '-'
            ratt_str = f"{row['rattrapage']:.1f}" if row['rattrapage'] is not None else '-'
            
            table_data.append([
                Paragraph(row['code_ec'], table_cell_style),
                Paragraph(row['intitule_ue'], table_cell_style),
                Paragraph(row['intitule_ec'], table_cell_style),
                Paragraph(row['categorie'], table_cell_center),
                Paragraph(str(row['credit']), table_cell_center),
                Paragraph(cc_str, table_cell_center),
                Paragraph(exa_str, table_cell_center),
                Paragraph(note_str, table_cell_center),
                Paragraph(note_pd_str, table_cell_center),
                Paragraph(ratt_str, table_cell_center),
                Paragraph(row['statut'], table_cell_center)
            ])
    
    col_widths = [1.5*cm, 3.8*cm, 5.2*cm, 0.9*cm, 0.8*cm, 0.9*cm, 1.0*cm, 0.9*cm, 1.0*cm, 0.9*cm, 1.8*cm]
    
    cours_table = Table(table_data, colWidths=col_widths)
    cours_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (2, -1), 'LEFT'),
        ('ALIGN', (3, 1), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    
    elements.append(cours_table)
    elements.append(Spacer(1, 4*mm))
    
    # Tableaux récapitulatifs
    def _format_decimal(value):
        if value is None:
            return '-'
        return f"{value:.1f}"
    
    moyenne_str = _format_decimal(moyenne)
    
    # Décision du jury - basée sur les statuts du modèle Deliberation
    def _decision_for_deliberation(credits_valides, credits_total):
        if credits_valides >= credits_total:
            return 'Validé'
        elif credits_valides >= credits_total * 0.7:  # 70% ou plus = Compensable
            return 'Compensable'
        else:
            return 'Ajourné'
    
    decision_jury = _decision_for_deliberation(credits_valides, credits_total)
    
    # Ligne 1: Total crédits, crédits capitalisés, moyenne, mention
    def _mention_for_note(note):
        if note is None:
            return 'A déterminer'
        n = float(note)
        if n >= 16:
            return 'Très bien'
        elif n >= 14:
            return 'Bien'
        elif n >= 12:
            return 'Assez bien'
        elif n >= 10:
            return 'Passable'
        else:
            return 'Insuffisant'
    
    mention = _mention_for_note(moyenne)
    
    summary1 = Table([
        [Paragraph('<b>Total crédits</b>', table_cell_style),
         Paragraph(str(credits_total), table_cell_center),
         Paragraph('<b>Crédits capitalisés</b>', table_cell_style),
         Paragraph(str(credits_valides), table_cell_center),
         Paragraph('<b>Moyenne</b>', table_cell_style),
         Paragraph(moyenne_str, table_cell_center),
         Paragraph('<b>Mention</b>', table_cell_style),
         Paragraph(mention, table_cell_center)]
    ], colWidths=[3*cm, 1.2*cm, 3.8*cm, 1.2*cm, 2*cm, 1.2*cm, 2*cm, 3.6*cm])
    summary1.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(summary1)
    elements.append(Spacer(1, 2*mm))
    
    # Ligne 2: Moyennes catégories et décision du jury
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
    
    # Construire le PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="profil_{etudiant.matricule_et}_{type_deliberation}.pdf"'
    return response
