from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings
import os


def generer_palmares_pdf(request, classe_obj, annee, etudiants_data, stats, titre_type="ANNUEL", classe_nom=""):
    """Génère le palmarès des résultats globaux en PDF avec ReportLab"""
    
    # Créer le buffer pour le PDF
    buffer = BytesIO()
    
    # Créer le document PDF en mode paysage
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    # Conteneur pour les éléments du document
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Style pour l'en-tête
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    
    # Style pour le titre principal
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=8,
        spaceBefore=4
    )
    
    # En-tête du document avec image PNG
    entete_path = os.path.join(settings.MEDIA_ROOT, 'entete.png')
    if os.path.exists(entete_path):
        from PIL import Image as PILImage
        pil_img = PILImage.open(entete_path)
        img_width, img_height = pil_img.size
        ratio = img_height / img_width
        desired_width = 24*cm
        desired_height = desired_width * ratio
        img = RLImage(entete_path, width=desired_width, height=desired_height)
        elements.append(img)
        elements.append(Spacer(1, 2*mm))
    
    # Titre principal
    titre = Paragraph(titre_type, title_style)
    elements.append(titre)
    
    # Ajouter la classe juste en dessous du titre
    if classe_nom:
        # Style pour le texte de la classe
        classe_style = ParagraphStyle(
            'ClasseStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=10
        )
        
        classe_text = Paragraph(f"Classe: {classe_nom}", classe_style)
        elements.append(classe_text)
    else:
        elements.append(Spacer(1, 3*mm))
    
    # Statistiques
    stats_data = [
        ['STATISTIQUES', f"ADMIS : {stats.get('admis', 0)}", f"COMP : {stats.get('comp', 0)}", f"AJ : {stats.get('aj', 0)}"],
        ['', f"DEF : {stats.get('def', 0)}", f"TOTAL : {stats.get('total', 0)}", '']
    ]
    
    stats_table = Table(stats_data, colWidths=[6*cm, 5*cm, 5*cm, 5*cm])
    stats_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 4*mm))
    
    # Tableau des étudiants
    moyenne_label = 'MOYENNE'
    
    table_data = [[
        'N°', 'NOM ET POST NOM', 'SEXE', 'NATIONALITE', 'MATRICULE',
        moyenne_label, 'POURC\nENTAGE', 'CREDITS\nCAPITALISES',
        'DECISION', 'MENTION'
    ]]
    
    for idx, etudiant in enumerate(etudiants_data, 1):
        table_data.append([
            str(idx),
            etudiant.get('nom', ''),
            etudiant.get('sexe', ''),
            etudiant.get('nationalite', ''),
            etudiant.get('matricule', ''),
            etudiant.get('moyenne', ''),
            etudiant.get('pourcentage', ''),
            etudiant.get('credits_capitalises', ''),
            etudiant.get('decision', ''),
            etudiant.get('mention', '')
        ])
    
    # Largeurs des colonnes (augmentées)
    col_widths = [1*cm, 7*cm, 1.2*cm, 2.8*cm, 2.3*cm, 2.2*cm, 1.8*cm, 2.5*cm, 2*cm, 2.5*cm]
    
    result_table = Table(table_data, colWidths=col_widths)
    result_table.setStyle(TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        
        # Corps du tableau
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # N°
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Nom
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'), # Reste
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        
        # Grille
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    
    elements.append(result_table)
    elements.append(Spacer(1, 1*cm))
    
    # Date et lieu
    from datetime import datetime
    date_str = datetime.now().strftime("%d/%m/%Y")
    
    # Style pour la date
    right_style = ParagraphStyle(
        'RightStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.black,
        alignment=TA_RIGHT,
        fontName='Helvetica',
        leftIndent=2*cm  # Déplacer vers l'intérieur
    )
    
    fait_a = Paragraph(f"Fait à .................................................. le {date_str}", right_style)
    elements.append(fait_a)
    elements.append(Spacer(1, 0.8*cm))
    
    # Récupérer les membres du jury de la classe
    from core.models import Jury, Enseignant
    try:
        jury = Jury.objects.filter(code_classe=classe_obj).first()
        if jury:
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
        fontSize=11,
        alignment=TA_CENTER,
        fontName='Helvetica',
    )
    
    # Style pour le grade en italique
    italic_style = ParagraphStyle(
        'ItalicStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
    )
    
    # Style pour les titres
    center_style = ParagraphStyle(
        'CenterStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
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
    
    # Construire le PDF
    doc.build(elements)
    
    # Retourner la réponse HTTP
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="palmares_{classe_obj.code_classe}_{annee}.pdf"'
    
    return response
