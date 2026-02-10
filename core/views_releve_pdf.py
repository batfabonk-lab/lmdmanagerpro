from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from .models import Inscription, Etudiant, Deliberation
from .utils_releve_pdf import generer_releve_pdf


@login_required
def jury_imprimable_releve(request, matricule):
    """Génère le relevé de notes d'un étudiant en PDF avec ReportLab - données depuis Deliberation"""
    from .views import get_jury_for_user, _require_deliberation_for_imprimable, _jury_compute_delib_ues
    
    jury = get_jury_for_user(request)
    if not jury:
        messages.error(request, 'Profil jury non trouvé.')
        return redirect('jury_imprimables')

    classe_obj = jury.code_classe
    classe_code = request.GET.get('classe', '')
    if request.user.is_staff and classe_code:
        from reglage.models import Classe
        classe_tmp = Classe.objects.filter(code_classe=classe_code).first()
        if classe_tmp:
            classe_obj = classe_tmp

    annee = request.GET.get('annee', '')

    selected_type = request.GET.get('type', 'annuel')
    selected_semestre = request.GET.get('semestre', '')
    if not _require_deliberation_for_imprimable(request, jury, classe_obj, annee, selected_type, selected_semestre):
        return redirect('jury_imprimables')
    
    # Récupérer l'étudiant
    try:
        etudiant = Etudiant.objects.get(matricule_et=matricule)
    except Etudiant.DoesNotExist:
        messages.error(request, 'Étudiant non trouvé.')
        return redirect('jury_imprimables')
    
    # Vérifier l'inscription
    inscription = Inscription.objects.filter(
        matricule_etudiant=etudiant,
        code_classe=classe_obj
    )
    if annee:
        inscription = inscription.filter(annee_academique=annee)
    
    inscription = inscription.first()
    if not inscription:
        messages.error(request, 'Inscription non trouvée.')
        return redirect('jury_imprimables')
    
    # Déterminer le semestre
    semestre_int = None
    if selected_type == 'semestriel' and selected_semestre and str(selected_semestre).isdigit():
        semestre_int = int(selected_semestre)
    
    # Calculer les détails des UE/EC depuis _jury_compute_delib_ues
    type_delib = selected_type
    delib_ues = _jury_compute_delib_ues(classe_obj, etudiant, type_delib, semestre_int, annee)
    
    # Vérifier qu'il y a des données
    if not delib_ues.get('rows'):
        messages.error(request, 'Aucune délibération trouvée pour cet étudiant.')
        return redirect('jury_imprimables')
    
    # Préparer les données de l'étudiant
    etudiant_data = {
        'nom': etudiant.nom_complet or '',
        'matricule': etudiant.matricule_et or '',
        'sexe': etudiant.sexe or '',
        'lieu_naissance': getattr(etudiant, 'lieu_naissance', ''),
        'date_naissance': getattr(etudiant, 'date_naissance', ''),
        'mention': 'Informatique de gestion (Conception des systèmes d\'informations)',
        'moyenne': delib_ues.get('moyenne'),
        'moyenne_cat_a': delib_ues.get('moyenne_cat_a'),
        'moyenne_cat_b': delib_ues.get('moyenne_cat_b'),
        'credits_total': delib_ues.get('credits_total', 0),
        'credits_valides': delib_ues.get('credits_valides', 0),
        'decision': delib_ues.get('decision_label', ''),
        'decision_code': delib_ues.get('decision_code', ''),
    }
    
    # Préparer les données des cours depuis delib_ues
    cours_data = []
    rows = delib_ues.get('rows', [])
    for row in rows:
        elements_list = row.get('elements', [])
        ec_details = row.get('ec_details', [])
        
        if not elements_list:
            elements_list = ['-']
        
        for idx, ec_name in enumerate(elements_list):
            code_ue = str(row.get('code', ''))
            intitule_ue = str(row.get('intitule', ''))
            categorie = str(row.get('categorie', '') or '')
            credit = row.get('credit', '') or ''
            
            cc_val = row.get('cc')
            exa_val = row.get('exa')
            note_val = row.get('note')
            note_pd_val = row.get('note_ponderee')
            ratt_val = row.get('rattrapage')
            statut = str(row.get('statut', '') or '')
            
            # Si on a des détails EC, utiliser les notes de l'EC
            if ec_details and idx < len(ec_details):
                ec_info = ec_details[idx]
                cc_val = ec_info.get('cc', cc_val)
                exa_val = ec_info.get('exa', exa_val)
                note_val = ec_info.get('note', note_val)
                note_pd_val = ec_info.get('note_ponderee', note_pd_val)
                ratt_val = ec_info.get('rattrapage', ratt_val)
                if ec_info.get('categorie'):
                    categorie = str(ec_info.get('categorie'))
                if ec_info.get('credit'):
                    credit = ec_info.get('credit')
                if ec_info.get('statut'):
                    statut = str(ec_info.get('statut'))
            
            cours_data.append({
                'code_ue': code_ue,
                'intitule_ue': intitule_ue,
                'intitule_ec': ec_name if ec_name else '-',
                'categorie': categorie,
                'credits_ec': credit,
                'cc': cc_val,
                'exa': exa_val,
                'note_session': note_val,
                'note_ponderee': note_pd_val,
                'note_rattrapage': ratt_val,
                'etat': statut,
            })
    
    # Générer le PDF (passer l'objet etudiant directement et les données de délibération)
    return generer_releve_pdf(request, etudiant, classe_obj, annee, semestre_int, delib_ues)
