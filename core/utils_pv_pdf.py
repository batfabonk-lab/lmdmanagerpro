from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
import os


def generer_pv_pdf(request, classe_obj, annee, session, date_delib, decision_ref, observations, presences_data, nb_etudiants=0):
    """Génère le PV de délibération en PDF avec ReportLab selon le modèle fourni"""
    
    # Créer le buffer pour le PDF
    buffer = BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Conteneur pour les éléments du document
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Style pour l'en-tête
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=4
    )
    
    header_small_style = ParagraphStyle(
        'HeaderSmallStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=2
    )
    
    # Style pour le titre principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=13,
        textColor=colors.black,
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        backColor=colors.lightgrey,
        borderPadding=8
    )
    
    # Style pour les sous-titres
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=5,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    # Style pour le texte normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=5,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    # Style pour le texte justifié
    justify_style = ParagraphStyle(
        'CustomJustify',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Style pour les sections avec fond gris
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=8,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        backColor=colors.lightgrey,
        borderPadding=6
    )
    
    # En-tête du document avec image PNG
    entete_path = os.path.join(settings.MEDIA_ROOT, 'entete.png')
    if os.path.exists(entete_path):
        from PIL import Image as PILImage
        pil_img = PILImage.open(entete_path)
        img_width, img_height = pil_img.size
        ratio = img_height / img_width
        desired_width = 17*cm
        desired_height = desired_width * ratio
        img = RLImage(entete_path, width=desired_width, height=desired_height)
        elements.append(img)
        elements.append(Spacer(1, 3*mm))
    
    # Titre principal
    titre = Paragraph("Procès verbal de délibération des résultats", title_style)
    elements.append(titre)
    elements.append(Spacer(1, 0.3*cm))
    
    # Informations générales
    info_data = [
        [Paragraph(f"<b>Année académique :</b> {annee}", normal_style), 
         Paragraph(f"<b>Session de :</b> {session}", normal_style)]
    ]
    info_table = Table(info_data, colWidths=[9*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.2*cm))
    
    # Classe
    classe_para = Paragraph(f"<b>Classe :</b> {classe_obj.code_classe} {classe_obj.designation_classe if hasattr(classe_obj, 'designation_classe') else ''}", normal_style)
    elements.append(classe_para)
    elements.append(Spacer(1, 0.4*cm))
    
    # Section Membres du jury
    membres_titre = Paragraph("Membres du jury", section_style)
    elements.append(membres_titre)
    elements.append(Spacer(1, 0.2*cm))
    
    # Tableau des membres du jury avec présences
    jury_data = []
    
    # Style compact pour le tableau
    compact_style = ParagraphStyle(
        'CompactStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=0,
        spaceBefore=0,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=10  # Interligne réduit
    )
    
    for presence in presences_data:
        statut_text = "Présent(e)" if presence['statut'] == 'present' else ("Absent(e)" if presence['statut'] == 'absent' else "Excusé(e)")
        jury_data.append([
            Paragraph(presence['nom'], compact_style),
            Paragraph(statut_text, compact_style)
        ])
    
    if jury_data:
        jury_table = Table(jury_data, colWidths=[12*cm, 5*cm])
        jury_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(jury_table)
    
    elements.append(Spacer(1, 0.5*cm))
    
    # Section Délibération
    delib_titre = Paragraph("Délibération :", section_style)
    elements.append(delib_titre)
    elements.append(Spacer(1, 0.2*cm))
    
    # Texte de délibération
    mois_annee = date_delib.strftime('%B %Y') if date_delib else ''
    
    delib_text = f"""Le jury chargé de procéder à l'organisation des examens de la session d'{session} de l'année académique {annee} par la décision n° {decision_ref} du {date_delib.strftime('%d %B %Y') if date_delib else ''} du Directeur Général de l'ISTAT/GM (Institut Supérieur des Techniques Appliquées de Gombe Matadi) a reçu les examens de {nb_etudiants} étudiant(s) en {classe_obj.code_classe} {classe_obj.designation_classe if hasattr(classe_obj, 'designation_classe') else ''}"""
    
    delib_para = Paragraph(delib_text, justify_style)
    elements.append(delib_para)
    
    # Texte après délibération
    apres_delib = Paragraph(
        "Après délibération à huis clos, le jury a pris les décisions suivantes : (Cf. Palmarès en annexe)",
        justify_style
    )
    elements.append(apres_delib)
    elements.append(Spacer(1, 0.5*cm))
    
    # Section Observations du jury
    if observations:
        obs_titre = Paragraph("Observations du jury :", section_style)
        elements.append(obs_titre)
        elements.append(Spacer(1, 0.2*cm))
        
        obs_para = Paragraph(observations, justify_style)
        elements.append(obs_para)
    
    # Construire le PDF
    doc.build(elements)
    
    # Récupérer le contenu du buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Créer la réponse HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="PV_Deliberation_{classe_obj.code_classe}_{annee}.pdf"'
    response.write(pdf)
    
    return response
