from django.conf import settings
from core.models import Enseignant, Etudiant, Inscription, Jury


def institution_info(request):
    """Injecte les infos de l'institution dans tous les templates."""
    return {
        'institution_slug': getattr(request, 'institution_slug', None) or getattr(settings, 'INSTITUTION_SLUG', 'default'),
        'institution_name': getattr(request, 'institution_name', None) or getattr(settings, 'INSTITUTION_NAME', 'LMD Manager Pro'),
        'institution_domain': getattr(settings, 'INSTITUTION_DOMAIN', ''),
    }


def navbar_user_label(request):
    user = getattr(request, 'user', None)
    if not user or not getattr(user, 'is_authenticated', False):
        return {'navbar_user_label': '', 'jury_cohorte_label': ''}

    if getattr(user, 'role', None) != 'JURY':
        return {'navbar_user_label': user.username, 'jury_cohorte_label': ''}

    username = user.username or ''
    poste = 'Jury'
    matricule = None

    if username.startswith('jury_pres_'):
        poste = 'Président'
        matricule = username.replace('jury_pres_', '', 1)
    elif username.startswith('jury_sec_'):
        poste = 'Secrétaire'
        matricule = username.replace('jury_sec_', '', 1)

    nom = None
    if matricule:
        enseignant = Enseignant.objects.filter(matricule_en=matricule).first()
        if enseignant and enseignant.nom_complet:
            nom = enseignant.nom_complet

    if not nom:
        nom = user.get_full_name().strip() or user.username

    jury_cohorte_label = ''
    jury = Jury.objects.filter(id_lgn=user).select_related('code_classe').first()
    if not jury:
        if username.startswith('jury_pres_') and matricule:
            jury = Jury.objects.filter(president=matricule).select_related('code_classe').first()
        elif username.startswith('jury_sec_') and matricule:
            jury = Jury.objects.filter(secretaire=matricule).select_related('code_classe').first()

    if jury and jury.code_classe:
        cohortes = list(
            Inscription.objects.filter(code_classe=jury.code_classe)
            .values_list('annee_academique', flat=True)
            .distinct()
        )
        if len(cohortes) == 1:
            jury_cohorte_label = f"Année: {cohortes[0]}"
        elif len(cohortes) > 1:
            jury_cohorte_label = ", ".join([str(a) for a in cohortes if a])

    return {
        'navbar_user_label': f"{poste} {nom}".strip(),
        'jury_cohorte_label': jury_cohorte_label,
    }


def sidebar_etudiant_profile(request):
    user = getattr(request, 'user', None)
    if not user or not getattr(user, 'is_authenticated', False):
        return {}

    etudiant = None
    is_simulation = False

    if getattr(user, 'is_staff', False) and request.session.get('simulated_etudiant'):
        etudiant = Etudiant.objects.filter(matricule_et=request.session.get('simulated_etudiant')).first()
        is_simulation = True
    elif getattr(user, 'role', None) == 'ETUDIANT':
        etudiant = Etudiant.objects.filter(id_lgn=user).first()

    if not etudiant:
        return {}

    from reglage.models import AnneeAcademique

    annee_active = AnneeAcademique.get_annee_en_cours()
    annee_code = annee_active.code_anac if annee_active else None

    inscriptions = Inscription.objects.filter(matricule_etudiant=etudiant).select_related('code_classe')
    inscription_active = None

    if annee_code:
        inscription_active = inscriptions.filter(annee_academique=annee_code).first()
    if not inscription_active:
        inscription_active = inscriptions.order_by('-annee_academique').first()

    return {
        'sidebar_etudiant': etudiant,
        'sidebar_etudiant_inscription': inscription_active,
        'sidebar_etudiant_is_simulation': is_simulation,
    }
