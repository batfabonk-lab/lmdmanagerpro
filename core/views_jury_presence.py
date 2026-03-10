from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from .models import Attribution, Enseignant, Inscription, Classe, UE, EC, Evaluation
from .models_presence import PresenceDeliberation
from .utils_pv_pdf import generer_pv_pdf
from reglage.models import Classe as ReglClasse
from .views import _require_deliberation_for_imprimable, _jury_compute_delib_ues


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


def get_jury_for_user(request):
    """Helper pour récupérer le jury"""
    from .models import Jury
    if request.user.is_staff and 'simulated_jury' in request.session:
        return Jury.objects.select_related('code_classe').filter(code_jury=request.session['simulated_jury']).first()
    jury = Jury.objects.filter(id_lgn=request.user).first()
    if not jury:
        jury = Jury.objects.select_related('code_classe').first()
    return jury


@login_required
def jury_presence_deliberation(request):
    """Formulaire de présence des enseignants à la délibération"""
    jury = get_jury_for_user(request)
    if not jury:
        messages.error(request, 'Profil jury non trouvé.')
        logout(request)
        return redirect('login')
    
    classe_code = request.GET.get('classe', '')
    annee = request.GET.get('annee', '')
    
    classe_obj = jury.code_classe
    if request.user.is_staff and classe_code:
        classe_tmp = Classe.objects.filter(code_classe=classe_code).first()
        if classe_tmp:
            classe_obj = classe_tmp
    
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        session = request.POST.get('session', 'Aout 2025')
        date_delib_str = request.POST.get('date_deliberation')
        decision_ref = request.POST.get('decision_reference', '')
        observations = request.POST.get('observations', '')
        
        if not date_delib_str:
            messages.error(request, 'Veuillez saisir la date de délibération.')
            return redirect(request.path + f'?classe={classe_code}&annee={annee}')
        
        date_delib = datetime.strptime(date_delib_str, '%Y-%m-%d').date()
        
        # Enregistrer les présences
        presences_data = []
        for key, value in request.POST.items():
            if key.startswith('presence_'):
                matricule = key.replace('presence_', '')
                try:
                    enseignant = Enseignant.objects.get(matricule_en=matricule)
                    # Supprimer l'ancienne présence si elle existe
                    PresenceDeliberation.objects.filter(
                        code_classe=classe_obj,
                        annee_academique=annee,
                        matricule_en=enseignant,
                        date_deliberation=date_delib
                    ).delete()
                    
                    # Créer la nouvelle présence
                    presence = PresenceDeliberation.objects.create(
                        code_classe=classe_obj,
                        annee_academique=annee,
                        session=session,
                        matricule_en=enseignant,
                        statut=value,
                        date_deliberation=date_delib,
                        observations=observations,
                        decision_reference=decision_ref,
                        enregistre_par=request.user
                    )
                    presences_data.append({
                        'nom': enseignant.nom_complet,
                        'statut': value
                    })
                except Enseignant.DoesNotExist:
                    pass
        
        if action == 'generate_pv':
            # Calculer le nombre d'étudiants de la classe pour cette année
            from .models import Inscription
            nb_etudiants = Inscription.objects.filter(
                code_classe=classe_obj,
                annee_academique=annee
            ).count()
            
            # Générer le PV en PDF
            return generer_pv_pdf(request, classe_obj, annee, session, date_delib, decision_ref, observations, presences_data, nb_etudiants)
        
        messages.success(request, 'Présences enregistrées avec succès!')
        return redirect('jury_imprimables')
    
    # Récupérer les codes de cours (UE et EC) de la classe
    from .models import UE, EC
    ue_codes = list(UE.objects.filter(classe=classe_obj).values_list('code_ue', flat=True))
    ec_codes = list(EC.objects.filter(classe=classe_obj).values_list('code_ec', flat=True))
    cours_codes = ue_codes + ec_codes
    
    # Récupérer les attributions pour ces cours
    attributions = Attribution.objects.filter(
        code_cours__in=cours_codes
    ).select_related('matricule_en', 'matricule_en__grade')
    
    if annee:
        attributions = attributions.filter(annee_academique=annee)
    
    enseignants = []
    seen_matricules = set()
    for attr in attributions:
        if attr.matricule_en and attr.matricule_en.matricule_en not in seen_matricules:
            enseignants.append({
                'matricule': attr.matricule_en.matricule_en,
                'nom': attr.matricule_en.nom_complet,
                'grade': attr.matricule_en.grade.designation_grade if attr.matricule_en.grade else 'N/A'
            })
            seen_matricules.add(attr.matricule_en.matricule_en)
    
    enseignants.sort(key=lambda e: e['nom'])
    
    # Valeurs par défaut pour le formulaire
    from datetime import date
    import locale
    
    # Définir la locale en français pour obtenir le nom du mois
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'French')
        except:
            pass
    
    today = date.today()
    mois_annee = today.strftime('%B %Y').capitalize()  # Ex: Janvier 2026
    date_aujourdhui = today.isoformat()  # Format YYYY-MM-DD pour input date
    decision_dg = jury.decision if jury.decision else ''
    
    context = {
        'jury': jury,
        'classe': classe_obj,
        'annee': annee,
        'enseignants': enseignants,
        'session_defaut': mois_annee,
        'date_defaut': date_aujourdhui,
        'decision_defaut': decision_dg,
    }
    
    return render(request, 'jury/presence_deliberation.html', context)


@login_required
def jury_imprimable_releves_tous(request):
    """Compiler tous les relevés de notes des étudiants en un seul document PDF avec ReportLab"""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, PageBreak
    from django.conf import settings
    import os
    from PIL import Image as PILImage
    
    jury = get_jury_for_user(request)
    if not jury:
        messages.error(request, 'Profil jury non trouvé.')
        return redirect('jury_imprimables')
    
    classe_code = request.GET.get('classe', '')
    annee = request.GET.get('annee', '')
    type_delib = request.GET.get('type', 'annuel')
    semestre_str = request.GET.get('semestre', '')
    semestre = int(semestre_str) if semestre_str and semestre_str.isdigit() else None
    
    classe_obj = jury.code_classe
    if request.user.is_staff and classe_code:
        classe_tmp = Classe.objects.filter(code_classe=classe_code).first()
        if classe_tmp:
            classe_obj = classe_tmp
    
    # Vérifier que la délibération existe
    if not _require_deliberation_for_imprimable(request, jury, classe_obj, annee, type_delib, str(semestre) if semestre else ''):
        return redirect('jury_imprimables')
    
    inscriptions = Inscription.objects.filter(code_classe=classe_obj).select_related('matricule_etudiant')
    if annee:
        inscriptions = inscriptions.filter(annee_academique=annee)
    
    inscriptions = inscriptions.order_by('matricule_etudiant__nom_complet')
    
    if not inscriptions.exists():
        messages.warning(request, 'Aucun étudiant trouvé.')
        return redirect('jury_imprimables')
    
    # Créer le buffer pour le PDF
    buffer = BytesIO()
    
    # Créer le document PDF
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
    
    # Styles pour les éléments
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.black,
        alignment=TA_LEFT,
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
    
    # Générer un relevé pour chaque étudiant
    for idx, inscription in enumerate(inscriptions):
        etudiant = inscription.matricule_etudiant
        
        # Ajouter un saut de page entre les relevés (sauf pour le premier)
        if idx > 0:
            elements.append(PageBreak())
        
        # En-tête avec image PNG
        entete_path = os.path.join(settings.MEDIA_ROOT, 'entete.png')
        if os.path.exists(entete_path):
            pil_img = PILImage.open(entete_path)
            img_width, img_height = pil_img.size
            ratio = img_height / img_width
            desired_width = 18*cm
            desired_height = desired_width * ratio
            from reportlab.platypus import Image as RLImage
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
        
        title = Paragraph("<b>RELEVÉ DES NOTES</b>", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*cm))
        
        # Infos étudiant
        nom_complet = getattr(etudiant, 'nom_complet', '') or f"{getattr(etudiant, 'nom_et', '')} {getattr(etudiant, 'postnom_et', '')} {getattr(etudiant, 'prenom_et', '')}"
        matricule = etudiant.matricule_et
        classe_label = getattr(classe_obj, 'code_classe', '')
        semestre_txt = f"S{semestre}" if semestre else ""
        
        # Tableau d'en-tête
        info_table = Table([
            [Paragraph("<b>Matricule :</b>", normal_style),
             Paragraph(f"{matricule}", normal_style),
             Paragraph("<b>Année académique :</b>", normal_style),
             Paragraph(f"{annee}", normal_style)],
            [Paragraph("<b>Noms :</b>", normal_style),
             Paragraph(f"{nom_complet}", normal_style),
             Paragraph("<b>Classe :</b>", normal_style),
             Paragraph(f"{classe_label}", normal_style)]
        ], colWidths=[2.5*cm, 4*cm, 3.5*cm, 4*cm])
        
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
        
        # Récupérer les données du relevé
        donnees = _jury_compute_delib_ues(classe_obj, etudiant, type_delib, semestre, annee)
        
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
        
        # Ajouter les cours
        rows = donnees.get('rows', [])
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
        
        # Largeurs colonnes
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
        credits_total = donnees.get('credits_total', 0)
        credits_valides = donnees.get('credits_valides', 0)
        moyenne = donnees.get('moyenne')
        moyenne_str = _format_decimal(moyenne)
        decision_label_calc = donnees.get('decision_label')
        decision_code_calc = donnees.get('decision_code')
        
        # Fonctions pour la décision et mention
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
            if credits_valides is None:
                return 'A déterminer'
            
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
        
        # Premier tableau récapitulatif
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
        
        # Deuxième tableau récapitulatif
        moyenne_cat_a = donnees.get('moyenne_cat_a')
        moyenne_cat_b = donnees.get('moyenne_cat_b')
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
        fait_a = Paragraph(f"Fait à .................................................. le {date_str}", ParagraphStyle(
            'RightStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_RIGHT,
            fontName='Helvetica',
        ))
        elements.append(fait_a)
        elements.append(Spacer(1, 0.2*cm))
        
        # Signature
        signature_table = Table([
            [Paragraph("", normal_style), Paragraph("<b>Le Chef de Section</b>", normal_style)],
            [Paragraph("", normal_style), Paragraph("<br/><br/><br/>", normal_style)],
            [Paragraph("", normal_style), Paragraph("____________________", normal_style)]
        ], colWidths=[12*cm, 6*cm])
        
        signature_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
            ('BOX', (0, 0), (-1, -1), 0, colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(signature_table)
    
    # Construire le PDF
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    
    # Créer un nom de fichier avec le type
    type_str = f"S{semestre}" if semestre else "Annuel"
    filename = f"releves_tous_{classe_obj.code_classe}_{type_str}_{annee}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response


@login_required
def jury_imprimable_profils_tous(request):
    """Compiler tous les profils des étudiants en un seul document PDF avec ReportLab"""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, PageBreak
    from django.conf import settings
    import os
    from PIL import Image as PILImage
    
    jury = get_jury_for_user(request)
    if not jury:
        messages.error(request, 'Profil jury non trouvé.')
        return redirect('jury_imprimables')
    
    classe_code = request.GET.get('classe', '')
    annee = request.GET.get('annee', '')
    type_delib = request.GET.get('type', 'annuel')
    semestre_str = request.GET.get('semestre', '')
    semestre = int(semestre_str) if semestre_str and semestre_str.isdigit() else None
    
    classe_obj = jury.code_classe
    if request.user.is_staff and classe_code:
        classe_tmp = Classe.objects.filter(code_classe=classe_code).first()
        if classe_tmp:
            classe_obj = classe_tmp
    
    # Vérifier que la délibération existe
    if not _require_deliberation_for_imprimable(request, jury, classe_obj, annee, type_delib, str(semestre) if semestre else ''):
        return redirect('jury_imprimables')
    
    inscriptions = Inscription.objects.filter(code_classe=classe_obj).select_related('matricule_etudiant')
    if annee:
        inscriptions = inscriptions.filter(annee_academique=annee)
    
    inscriptions = inscriptions.order_by('matricule_etudiant__nom_complet')
    
    if not inscriptions.exists():
        messages.warning(request, 'Aucun étudiant trouvé.')
        return redirect('jury_imprimables')
    
    # Créer le buffer pour le PDF
    buffer = BytesIO()
    
    # Créer le document PDF
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
    
    # Styles pour les éléments
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
    
    # Générer un profil pour chaque étudiant
    for idx, inscription in enumerate(inscriptions):
        etudiant = inscription.matricule_etudiant
        
        # Ajouter un saut de page entre les profils (sauf pour le premier)
        if idx > 0:
            elements.append(PageBreak())
        
        # En-tête avec image PNG
        entete_path = os.path.join(settings.MEDIA_ROOT, 'entete.png')
        if os.path.exists(entete_path):
            pil_img = PILImage.open(entete_path)
            img_width, img_height = pil_img.size
            ratio = img_height / img_width
            desired_width = 18*cm
            desired_height = desired_width * ratio
            from reportlab.platypus import Image as RLImage
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
        matricule = etudiant.matricule_et
        classe_label = getattr(classe_obj, 'code_classe', '')
        
        # Déterminer le texte pour la période
        periode_txt = f"S{semestre}" if semestre else "Annuel"
        
        # Tableau d'en-tête
        info_table = Table([
            [Paragraph("<b>Matricule :</b>", right_style),
             Paragraph(f"{matricule}", normal_style),
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
        
        # Récupérer les données du profil
        donnees = _jury_compute_delib_ues(classe_obj, etudiant, type_delib, semestre, annee)
        
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
        
        # Ajouter les cours
        rows = donnees.get('rows', [])
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
        
        # Largeurs colonnes
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
        credits_total = donnees.get('credits_total', 0)
        credits_valides = donnees.get('credits_valides', 0)
        moyenne = donnees.get('moyenne')
        moyenne_str = _format_decimal(moyenne)
        decision_label_calc = donnees.get('decision_label')
        decision_code_calc = donnees.get('decision_code')
        
        # Fonctions pour la décision et mention
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
            if credits_valides is None:
                return 'A déterminer'
            
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
        
        # Premier tableau récapitulatif
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
        
        # Deuxième tableau récapitulatif
        moyenne_cat_a = donnees.get('moyenne_cat_a')
        moyenne_cat_b = donnees.get('moyenne_cat_b')
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
        elements.append(Spacer(1, 0.8*cm))
        
        # Section des signataires (3 colonnes) avec les noms soulignés et grades en italique
        # Récupérer les membres du jury de la classe
        from .models import Jury, Enseignant
        try:
            jury_obj = Jury.objects.filter(code_classe=classe_obj, annee_academique=annee).first()
            if jury_obj:
                # Membre du jury
                if jury_obj.membre:
                    try:
                        enseignant_membre = Enseignant.objects.get(matricule_en=jury_obj.membre)
                        membre_nom = enseignant_membre.nom_complet
                        membre_grade = enseignant_membre.grade.designation_grade if enseignant_membre.grade else "Grade: _______________"
                    except:
                        membre_nom = jury_obj.membre
                        membre_grade = "Grade: _______________"
                else:
                    membre_nom = "____________________"
                    membre_grade = "Grade: _______________"
                
                # Président du jury
                if jury_obj.president:
                    try:
                        enseignant_president = Enseignant.objects.get(matricule_en=jury_obj.president)
                        president_nom = enseignant_president.nom_complet
                        president_grade = enseignant_president.grade.designation_grade if enseignant_president.grade else "Grade: _______________"
                    except:
                        president_nom = jury_obj.president
                        president_grade = "Grade: _______________"
                else:
                    president_nom = "____________________"
                    president_grade = "Grade: _______________"
                
                # Secrétaire du jury
                if jury_obj.secretaire:
                    try:
                        enseignant_secretaire = Enseignant.objects.get(matricule_en=jury_obj.secretaire)
                        secretaire_nom = enseignant_secretaire.nom_complet
                        secretaire_grade = enseignant_secretaire.grade.designation_grade if enseignant_secretaire.grade else "Grade: _______________"
                    except:
                        secretaire_nom = jury_obj.secretaire
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
    
    # Construire le PDF
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    
    # Créer un nom de fichier avec le type
    type_str = f"S{semestre}" if semestre else "Annuel"
    filename = f"profils_tous_{classe_obj.code_classe}_{type_str}_{annee}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response


@login_required
def jury_imprimable_releves_selectionnes(request):
    """Compiler les relevés de notes des étudiants sélectionnés en un seul document PDF"""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, PageBreak
    from django.conf import settings
    import os
    from PIL import Image as PILImage
    
    jury = get_jury_for_user(request)
    if not jury:
        messages.error(request, 'Profil jury non trouvé.')
        return redirect('jury_imprimables')
    
    # Récupérer les paramètres
    classe_code = request.GET.get('classe', '')
    annee = request.GET.get('annee', '')
    type_delib = request.GET.get('type', 'annuel')
    semestre_str = request.GET.get('semestre', '')
    matricules_str = request.GET.get('matricules', '')
    
    semestre = int(semestre_str) if semestre_str and semestre_str.isdigit() else None
    
    classe_obj = jury.code_classe
    if request.user.is_staff and classe_code:
        classe_tmp = Classe.objects.filter(code_classe=classe_code).first()
        if classe_tmp:
            classe_obj = classe_tmp
    
    # Vérifier que la délibération existe
    if not _require_deliberation_for_imprimable(request, jury, classe_obj, annee, type_delib, str(semestre) if semestre else ''):
        return redirect('jury_imprimables')
    
    # Récupérer les matricules sélectionnés
    if not matricules_str:
        messages.error(request, 'Aucun étudiant sélectionné.')
        return redirect('jury_imprimables')
    
    matricules = [m.strip() for m in matricules_str.split(',') if m.strip()]
    
    # Récupérer les inscriptions des étudiants sélectionnés
    inscriptions = Inscription.objects.filter(
        code_classe=classe_obj,
        matricule_etudiant__matricule_et__in=matricules
    ).select_related('matricule_etudiant')
    
    if annee:
        inscriptions = inscriptions.filter(annee_academique=annee)
    
    inscriptions = inscriptions.order_by('matricule_etudiant__nom_complet')
    
    if not inscriptions.exists():
        messages.warning(request, 'Aucun étudiant trouvé parmi la sélection.')
        return redirect('jury_imprimables')
    
    # Créer le buffer pour le PDF
    buffer = BytesIO()
    
    # Créer le document PDF
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
    
    # Styles pour les éléments
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.black,
        alignment=TA_LEFT,
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
    
    # Générer un relevé pour chaque étudiant sélectionné
    for idx, inscription in enumerate(inscriptions):
        etudiant = inscription.matricule_etudiant
        
        # Ajouter un saut de page entre les relevés (sauf pour le premier)
        if idx > 0:
            elements.append(PageBreak())
        
        # En-tête avec image PNG
        entete_path = os.path.join(settings.MEDIA_ROOT, 'entete.png')
        if os.path.exists(entete_path):
            pil_img = PILImage.open(entete_path)
            img_width, img_height = pil_img.size
            ratio = img_height / img_width
            desired_width = 18*cm
            desired_height = desired_width * ratio
            from reportlab.platypus import Image as RLImage
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
        
        title = Paragraph("<b>RELEVÉ DES NOTES</b>", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*cm))
        
        # Infos étudiant
        nom_complet = getattr(etudiant, 'nom_complet', '') or f"{getattr(etudiant, 'nom_et', '')} {getattr(etudiant, 'postnom_et', '')} {getattr(etudiant, 'prenom_et', '')}"
        matricule = etudiant.matricule_et
        classe_label = getattr(classe_obj, 'code_classe', '')
        
        # Tableau d'en-tête
        info_table = Table([
            [Paragraph("<b>Matricule :</b>", normal_style),
             Paragraph(f"{matricule}", normal_style),
             Paragraph("<b>Année académique :</b>", normal_style),
             Paragraph(f"{annee}", normal_style)],
            [Paragraph("<b>Noms :</b>", normal_style),
             Paragraph(f"{nom_complet}", normal_style),
             Paragraph("<b>Classe :</b>", normal_style),
             Paragraph(f"{classe_label}", normal_style)]
        ], colWidths=[2.5*cm, 4*cm, 3.5*cm, 4*cm])
        
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
        
        # Récupérer les données du relevé via _jury_compute_delib_ues (aligné avec modèle Deliberation)
        donnees = _jury_compute_delib_ues(classe_obj, etudiant, type_delib, semestre, annee)
        
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
        
        # Ajouter les cours
        rows = donnees.get('rows', [])
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
        
        # Largeurs colonnes
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
        credits_total = donnees.get('credits_total', 0)
        credits_valides = donnees.get('credits_valides', 0)
        moyenne = donnees.get('moyenne')
        moyenne_str = _format_decimal(moyenne)
        decision_label_calc = donnees.get('decision_label')
        decision_code_calc = donnees.get('decision_code')
        
        # Fonctions pour la décision et mention
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
            if credits_valides is None:
                return 'A déterminer'
            
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
        
        # Premier tableau récapitulatif
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
        
        # Deuxième tableau récapitulatif
        moyenne_cat_a = donnees.get('moyenne_cat_a')
        moyenne_cat_b = donnees.get('moyenne_cat_b')
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
        fait_a = Paragraph(f"Fait à .................................................. le {date_str}", ParagraphStyle(
            'RightStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_RIGHT,
            fontName='Helvetica',
        ))
        elements.append(fait_a)
        elements.append(Spacer(1, 0.2*cm))
        
        # Signature
        signature_table = Table([
            [Paragraph("", normal_style), Paragraph("<b>Le Chef de Section</b>", normal_style)],
            [Paragraph("", normal_style), Paragraph("<br/><br/><br/>", normal_style)],
            [Paragraph("", normal_style), Paragraph("____________________", normal_style)]
        ], colWidths=[12*cm, 6*cm])
        
        signature_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
            ('BOX', (0, 0), (-1, -1), 0, colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(signature_table)
    
    # Construire le PDF
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    
    # Créer un nom de fichier avec le premier étudiant et le type
    premier_etudiant = inscriptions.first().matricule_etudiant if inscriptions.exists() else None
    if premier_etudiant:
        nom_etudiant = premier_etudiant.nom_complet or f"{premier_etudiant.nom_et or ''} {premier_etudiant.postnom_et or ''} {premier_etudiant.prenom_et or ''}".strip()
        # Nettoyer le nom pour le fichier
        nom_etudiant = nom_etudiant.replace(" ", "_").replace("/", "_").replace("\\", "_")
        
        if len(inscriptions) == 1:
            filename = f"releve_{nom_etudiant}_S{semestre}_{annee}.pdf" if semestre else f"releve_{nom_etudiant}_Annuel_{annee}.pdf"
        else:
            type_str = f"S{semestre}" if semestre else "Annuel"
            filename = f"releves_selectionnes_{len(inscriptions)}etudiants_{type_str}_{annee}.pdf"
    else:
        filename = f"releves_selectionnes_{classe_obj.code_classe}_{annee}.pdf"
    
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response


@login_required
def jury_imprimable_profils_selectionnes(request):
    """Compiler les profils des étudiants sélectionnés en un seul document PDF"""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, PageBreak
    from django.conf import settings
    import os
    from PIL import Image as PILImage
    
    jury = get_jury_for_user(request)
    if not jury:
        messages.error(request, 'Profil jury non trouvé.')
        return redirect('jury_imprimables')
    
    # Récupérer les paramètres
    classe_code = request.GET.get('classe', '')
    annee = request.GET.get('annee', '')
    type_delib = request.GET.get('type', 'annuel')
    semestre_str = request.GET.get('semestre', '')
    matricules_str = request.GET.get('matricules', '')
    
    semestre = int(semestre_str) if semestre_str and semestre_str.isdigit() else None
    
    classe_obj = jury.code_classe
    if request.user.is_staff and classe_code:
        classe_tmp = Classe.objects.filter(code_classe=classe_code).first()
        if classe_tmp:
            classe_obj = classe_tmp
    
    # Vérifier que la délibération existe
    if not _require_deliberation_for_imprimable(request, jury, classe_obj, annee, type_delib, str(semestre) if semestre else ''):
        return redirect('jury_imprimables')
    
    # Récupérer les matricules sélectionnés
    if not matricules_str:
        messages.error(request, 'Aucun étudiant sélectionné.')
        return redirect('jury_imprimables')
    
    matricules = [m.strip() for m in matricules_str.split(',') if m.strip()]
    
    # Récupérer les inscriptions des étudiants sélectionnés
    inscriptions = Inscription.objects.filter(
        code_classe=classe_obj,
        matricule_etudiant__matricule_et__in=matricules
    ).select_related('matricule_etudiant')
    
    if annee:
        inscriptions = inscriptions.filter(annee_academique=annee)
    
    inscriptions = inscriptions.order_by('matricule_etudiant__nom_complet')
    
    if not inscriptions.exists():
        messages.warning(request, 'Aucun étudiant trouvé parmi la sélection.')
        return redirect('jury_imprimables')
    
    # Créer le buffer pour le PDF
    buffer = BytesIO()
    
    # Créer le document PDF
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
    
    # Styles pour les éléments
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
    
    # Générer un profil pour chaque étudiant sélectionné
    for idx, inscription in enumerate(inscriptions):
        etudiant = inscription.matricule_etudiant
        
        # Ajouter un saut de page entre les profils (sauf pour le premier)
        if idx > 0:
            elements.append(PageBreak())
        
        # En-tête avec image PNG
        entete_path = os.path.join(settings.MEDIA_ROOT, 'entete.png')
        if os.path.exists(entete_path):
            pil_img = PILImage.open(entete_path)
            img_width, img_height = pil_img.size
            ratio = img_height / img_width
            desired_width = 18*cm
            desired_height = desired_width * ratio
            from reportlab.platypus import Image as RLImage
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
        matricule = etudiant.matricule_et
        classe_label = getattr(classe_obj, 'code_classe', '')
        
        # Déterminer le texte pour la période
        periode_txt = f"S{semestre}" if semestre else "Annuel"
        
        # Tableau d'en-tête
        info_table = Table([
            [Paragraph("<b>Matricule :</b>", right_style),
             Paragraph(f"{matricule}", normal_style),
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
        
        # Récupérer les données du profil
        donnees = _jury_compute_delib_ues(classe_obj, etudiant, type_delib, semestre, annee)
        
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
        
        # Ajouter les cours
        rows = donnees.get('rows', [])
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
        
        # Largeurs colonnes
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
        credits_total = donnees.get('credits_total', 0)
        credits_valides = donnees.get('credits_valides', 0)
        moyenne = donnees.get('moyenne')
        moyenne_str = _format_decimal(moyenne)
        decision_label_calc = donnees.get('decision_label')
        decision_code_calc = donnees.get('decision_code')
        
        # Fonctions pour la décision et mention
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
            if credits_valides is None:
                return 'A déterminer'
            
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
        
        # Premier tableau récapitulatif
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
        
        # Deuxième tableau récapitulatif
        moyenne_cat_a = donnees.get('moyenne_cat_a')
        moyenne_cat_b = donnees.get('moyenne_cat_b')
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
        elements.append(Spacer(1, 0.8*cm))
        
        # Section des signataires (3 colonnes) avec les noms soulignés et grades en italique
        # Récupérer les membres du jury de la classe
        from .models import Jury, Enseignant
        try:
            jury_obj = Jury.objects.filter(code_classe=classe_obj, annee_academique=annee).first()
            if jury_obj:
                # Membre du jury
                if jury_obj.membre:
                    try:
                        enseignant_membre = Enseignant.objects.get(matricule_en=jury_obj.membre)
                        membre_nom = enseignant_membre.nom_complet
                        membre_grade = enseignant_membre.grade.designation_grade if enseignant_membre.grade else "Grade: _______________"
                    except:
                        membre_nom = jury_obj.membre
                        membre_grade = "Grade: _______________"
                else:
                    membre_nom = "____________________"
                    membre_grade = "Grade: _______________"
                
                # Président du jury
                if jury_obj.president:
                    try:
                        enseignant_president = Enseignant.objects.get(matricule_en=jury_obj.president)
                        president_nom = enseignant_president.nom_complet
                        president_grade = enseignant_president.grade.designation_grade if enseignant_president.grade else "Grade: _______________"
                    except:
                        president_nom = jury_obj.president
                        president_grade = "Grade: _______________"
                else:
                    president_nom = "____________________"
                    president_grade = "Grade: _______________"
                
                # Secrétaire du jury
                if jury_obj.secretaire:
                    try:
                        enseignant_secretaire = Enseignant.objects.get(matricule_en=jury_obj.secretaire)
                        secretaire_nom = enseignant_secretaire.nom_complet
                        secretaire_grade = enseignant_secretaire.grade.designation_grade if enseignant_secretaire.grade else "Grade: _______________"
                    except:
                        secretaire_nom = jury_obj.secretaire
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
    
    # Construire le PDF
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    
    # Créer un nom de fichier avec le premier étudiant et le type
    premier_etudiant = inscriptions.first().matricule_etudiant if inscriptions.exists() else None
    if premier_etudiant:
        nom_etudiant = premier_etudiant.nom_complet or f"{premier_etudiant.nom_et or ''} {premier_etudiant.postnom_et or ''} {premier_etudiant.prenom_et or ''}".strip()
        # Nettoyer le nom pour le fichier
        nom_etudiant = nom_etudiant.replace(" ", "_").replace("/", "_").replace("\\", "_")
        
        if len(inscriptions) == 1:
            filename = f"profil_{nom_etudiant}_S{semestre}_{annee}.pdf" if semestre else f"profil_{nom_etudiant}_Annuel_{annee}.pdf"
        else:
            type_str = f"S{semestre}" if semestre else "Annuel"
            filename = f"profils_selectionnes_{len(inscriptions)}etudiants_{type_str}_{annee}.pdf"
    else:
        filename = f"profils_selectionnes_{classe_obj.code_classe}_{annee}.pdf"
    
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response


@login_required
def jury_imprimable_palmares_selectionnes(request):
    """Génère le palmarès PDF uniquement pour les étudiants sélectionnés"""
    from .utils_palmares_pdf import generer_palmares_pdf
    from .views import _require_deliberation_for_imprimable, _jury_compute_delib_ues

    jury = get_jury_for_user(request)
    if not jury:
        messages.error(request, 'Profil jury non trouvé.')
        return redirect('jury_imprimables')

    classe_obj = jury.code_classe
    classe_code = request.GET.get('classe', '')
    if request.user.is_staff and classe_code:
        classe_tmp = Classe.objects.filter(code_classe=classe_code).first()
        if classe_tmp:
            classe_obj = classe_tmp

    annee = request.GET.get('annee', '')
    selected_type = request.GET.get('type', 'annuel')
    selected_semestre = request.GET.get('semestre', '')
    matricules_str = request.GET.get('matricules', '')
    matricules = [m.strip() for m in matricules_str.split(',') if m.strip()]

    if not matricules:
        messages.warning(request, 'Aucun étudiant sélectionné.')
        return redirect('jury_imprimables')

    if not _require_deliberation_for_imprimable(request, jury, classe_obj, annee, selected_type, selected_semestre):
        return redirect('jury_imprimables')

    inscriptions = Inscription.objects.filter(
        code_classe=classe_obj,
        matricule_etudiant__matricule_et__in=matricules
    ).select_related('matricule_etudiant')
    if annee:
        inscriptions = inscriptions.filter(annee_academique=annee)

    if selected_type == 'semestriel':
        palmares_type = 'semestriel'
        palmares_semestre = int(selected_semestre) if selected_semestre else 1
    else:
        palmares_type = 'annuel'
        palmares_semestre = None

    def _mention_for_moyenne(moyenne):
        if moyenne is None:
            return 'A déterminer'
        n = float(moyenne)
        if n >= 18: return 'Excellent (A)'
        if n >= 16: return 'Très bien (B)'
        if n >= 14: return 'Bien (C)'
        if n >= 12: return 'Assez Bien (D)'
        if n >= 10: return 'Passable (E)'
        if n >= 8:  return 'Insuffisant (F)'
        return 'Insatisfaisant (G)'

    type_delib = 'annuel' if palmares_type == 'annuel' else 'semestriel'
    semestre_int = int(palmares_semestre) if palmares_semestre else None

    etudiants_data = []
    stats = {'admis': 0, 'comp': 0, 'aj': 0, 'def': 0, 'total': 0}

    for inscription in inscriptions:
        etudiant = inscription.matricule_etudiant
        delib_data = _jury_compute_delib_ues(classe_obj, etudiant, type_delib, semestre_int, annee)
        if not delib_data.get('rows'):
            continue

        moyenne = delib_data.get('moyenne', 0) or 0
        credits_capitalises = delib_data.get('credits_valides', 0)
        pourcentage = delib_data.get('pourcentage', 0) or 0
        decision_code = delib_data.get('decision_code')

        if decision_code == 'DEF':
            decision = 'DEF'; stats['def'] += 1
        elif decision_code == 'ADM':
            decision = 'ADM'; stats['admis'] += 1
        elif decision_code in ['ADMD', 'COMP']:
            decision = 'COMP'; stats['comp'] += 1
        else:
            decision = 'AJ'; stats['aj'] += 1

        stats['total'] += 1
        mention = _mention_for_moyenne(moyenne)

        etudiants_data.append({
            'nom': etudiant.nom_complet or '',
            'sexe': etudiant.sexe or '',
            'nationalite': etudiant.nationalite or '',
            'matricule': etudiant.matricule_et or '',
            'moyenne': f"{moyenne:.2f}".replace('.', ','),
            'pourcentage': f"{pourcentage:.1f}".replace('.', ',') + '%',
            'credits_capitalises': str(credits_capitalises),
            'decision': decision,
            'mention': mention,
        })

    etudiants_data.sort(key=lambda x: float(str(x['moyenne']).replace(',', '.')), reverse=True)

    if palmares_type == 'semestriel':
        titre_type = f"PALMARES DES RESULTATS SEMESTRE {palmares_semestre} {annee}"
    else:
        titre_type = f"PALMARES DES RESULTATS ANNUEL {annee}"

    classe_nom = classe_obj.code_classe if classe_obj else ''
    return generer_palmares_pdf(request, classe_obj, annee, etudiants_data, stats, titre_type, classe_nom)
