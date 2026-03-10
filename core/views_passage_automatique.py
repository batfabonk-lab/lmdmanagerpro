"""
Vue pour le passage automatique des étudiants à la classe supérieure.
Architecture V3 — corrigée et robuste :
- ADMIS (ADM) → Inscription classe supérieure
- COMPENSÉ (ADMD/COMP) → Inscription classe supérieure + InscriptionUE (dettes)
- AJOURNÉ/DÉFAILLANT (AJ/DEF) → Redoublement + Evaluation transférées (notes >= 10)

Seuils de diplôme :
  Licence  (fin L3) : >= 180 crédits cumulés (même mention)
  Master   (fin M2) : >= 120 crédits cumulés (même mention, cycle Master)
"""

import logging
from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

from django.db.models import Count
from .models import Inscription, Deliberation, Evaluation, Etudiant, Cohorte, InscriptionUE
from reglage.models import Classe, AnneeAcademique, Niveau

logger = logging.getLogger(__name__)

# Hiérarchie des niveaux LMD
_NIVEAU_SUIVANT = {
    'L1': 'L2',
    'L2': 'L3',
    'L3': 'M1',
    'M1': 'M2',
    'M2': None,   # fin de parcours
}

_NIVEAU_PRECEDENT = {
    'L1': None,   # pas de niveau inférieur
    'L2': 'L1',
    'L3': 'L2',
    'M1': None,   # début du cycle Master
    'M2': 'M1',
}

# Seuils de crédits pour les diplômes
SEUIL_LICENCE = 180   # L1+L2+L3
SEUIL_MASTER  = 120   # M1+M2


# ========== FONCTIONS UTILITAIRES ==========

def _get_classe_superieure(classe_actuelle):
    """
    Détermine la classe supérieure via code_niveau et code_mention.
    Retourne None si l'étudiant est en fin de cycle (M2).
    """
    niveau_actuel = classe_actuelle.code_niveau_id   # ex: 'L1'
    mention = classe_actuelle.code_mention_id         # ex: 'INFO'

    niveau_suivant_code = _NIVEAU_SUIVANT.get(niveau_actuel)
    if niveau_suivant_code is None:
        return None  # M2 → fin de parcours

    try:
        return Classe.objects.get(code_niveau_id=niveau_suivant_code, code_mention_id=mention)
    except Classe.DoesNotExist:
        logger.warning(f"Classe supérieure introuvable : niveau={niveau_suivant_code}, mention={mention}")
        return None


def _identifier_dettes_etudiant(etudiant, annee_academique):
    """
    Identifie les cours non validés (dettes) d'un étudiant.
    Retourne une liste de délibérations NON_VALIDE.
    """
    dettes = Deliberation.objects.filter(
        matricule_etudiant=etudiant,
        annee_academique=annee_academique,
        type_deliberation__in=['S1', 'S2'],
        statut='NON_VALIDE'
    ).select_related('code_ue', 'code_ec')
    
    return list(dettes)


def _marquer_dettes_liquidees(etudiant, mention_id=None):
    """
    Marque comme DETTE_LIQUIDEE toutes les InscriptionUE de type DETTE_COMPENSEE
    pour lesquelles une Deliberation VALIDE existe désormais.
    Retourne le nombre de dettes liquidées.
    """
    filtre = {
        'matricule_etudiant': etudiant,
        'type_inscription': 'DETTE_COMPENSEE',
    }
    if mention_id:
        filtre['code_classe__code_mention_id'] = mention_id
    
    all_dettes = InscriptionUE.objects.filter(**filtre).select_related('code_ue', 'code_ec')
    
    nb_liquidees = 0
    for dette in all_dettes:
        filtre_delib = {'matricule_etudiant': etudiant, 'statut': 'VALIDE'}
        if dette.code_ec:
            filtre_delib['code_ec'] = dette.code_ec
        elif dette.code_ue:
            filtre_delib['code_ue'] = dette.code_ue
        else:
            continue
        
        if Deliberation.objects.filter(**filtre_delib).exists():
            dette.type_inscription = 'DETTE_LIQUIDEE'
            dette.save(update_fields=['type_inscription'])
            nb_liquidees += 1
            logger.info(
                f"✅ DETTE LIQUIDÉE: {etudiant.matricule_et} - "
                f"{dette.code_ue.code_ue if dette.code_ue else dette.code_ec.code_ec}"
            )
    
    return nb_liquidees


def _get_dettes_L1_non_capitalisees(etudiant, mention_id):
    """
    Retourne les InscriptionUE (dettes compensées) de L1 de l'étudiant qui
    n'ont pas encore été capitalisées (aucune Deliberation VALIDE).
    
    Cette vérification est utilisée UNIQUEMENT au passage L2 → L3 :
    un étudiant ne peut PAS monter en L3 s'il a des dettes L1 non soldées.
    """
    # Filtrer uniquement les dettes dont la classe d'origine est de niveau L1
    all_dettes_l1 = InscriptionUE.objects.filter(
        matricule_etudiant=etudiant,
        type_inscription='DETTE_COMPENSEE',
        code_classe__code_niveau_id='L1',
        code_classe__code_mention_id=mention_id,
    ).select_related('code_ue', 'code_ec', 'code_classe')
    
    non_capitalisees = []
    for dette in all_dettes_l1:
        filtre = {'matricule_etudiant': etudiant, 'statut': 'VALIDE'}
        if dette.code_ec:
            filtre['code_ec'] = dette.code_ec
        elif dette.code_ue:
            filtre['code_ue'] = dette.code_ue
        else:
            continue
        
        if not Deliberation.objects.filter(**filtre).exists():
            non_capitalisees.append(dette)
    
    return non_capitalisees


def _calculer_credits_totaux_etudiant(etudiant, mention_id, niveaux_codes):
    """
    Calcule le total des crédits capitalisés par un étudiant
    dans une mention donnée et pour un ensemble de niveaux (cycle).
    
    Paramètres :
      mention_id    – code de la mention (ex: 'INFO')
      niveaux_codes – liste de niveaux à comptabiliser (ex: ['L1','L2','L3'])
    """
    # Filtrer les délibérations validées de la bonne mention + niveaux
    deliberations_validees = Deliberation.objects.filter(
        matricule_etudiant=etudiant,
        statut='VALIDE',
        code_classe__code_mention_id=mention_id,
        code_classe__code_niveau_id__in=niveaux_codes,
    ).select_related('code_ue', 'code_ec')
    
    credits_total = 0
    codes_comptes = set()  # éviter les doublons
    
    for delib in deliberations_validees:
        if delib.code_ec:
            key = f"EC-{delib.code_ec.code_ec}"
            if key not in codes_comptes:
                credits_total += delib.code_ec.credit or 0
                codes_comptes.add(key)
        elif delib.code_ue:
            key = f"UE-{delib.code_ue.code_ue}"
            if key not in codes_comptes:
                credits_total += delib.code_ue.credit or 0
                codes_comptes.add(key)
    
    return credits_total


def _trouver_cohorte_montante(classe, annee_code):
    """
    Pour un redoublant : trouver la cohorte « montante » de la classe inférieure.

    Principe : les étudiants du niveau N-1 (même mention) de l'année courante
    vont monter dans la même classe que le redoublant l'année suivante.
    Le redoublant rejoint cette cohorte-là.

    Exemple concret :
      Étudiant X : L2INFO / COH_INFO_2025 / 2025-2026 → AJ
      L1INFO a une cohorte COH_INFO_2026 en 2025-2026 qui va monter en L2INFO
      → X rejoint COH_INFO_2026 pour 2026-2027 en L2INFO

    Si aucune classe inférieure ou aucune cohorte trouvée, retourne None.
    """
    niveau_actuel = classe.code_niveau_id
    mention = classe.code_mention_id
    niveau_precedent_code = _NIVEAU_PRECEDENT.get(niveau_actuel)

    if niveau_precedent_code is None:
        # L1 ou M1 (début de cycle) : pas de classe inférieure
        logger.info(
            f"Pas de niveau précédent pour {classe.code_classe} "
            f"(début de cycle) — cohorte montante non applicable"
        )
        return None

    try:
        classe_inferieure = Classe.objects.get(
            code_niveau_id=niveau_precedent_code,
            code_mention_id=mention,
        )
    except Classe.DoesNotExist:
        logger.warning(f"Classe inférieure introuvable : niveau={niveau_precedent_code}, mention={mention}")
        return None

    # Chercher la cohorte la plus fréquente dans la classe inférieure
    # pour l'année en cours (ce sont eux qui vont monter)
    inscription_inf = (
        Inscription.objects.filter(
            code_classe=classe_inferieure,
            annee_academique=annee_code,
            cohorte__isnull=False,
        )
        .values('cohorte')
        .annotate(nb=Count('cohorte'))
        .order_by('-nb')
        .first()
    )

    if inscription_inf:
        cohorte_montante = Cohorte.objects.get(pk=inscription_inf['cohorte'])
        logger.info(
            f"Cohorte montante trouvée : {cohorte_montante.code_cohorte} "
            f"(de {classe_inferieure.code_classe} {annee_code})"
        )
        return cohorte_montante

    logger.warning(
        f"Aucune cohorte trouvée dans {classe_inferieure.code_classe} "
        f"pour {annee_code} — cohorte montante introuvable"
    )
    return None


def _trouver_ou_creer_cohorte_annee(mention_id, annee_suivante):
    """
    Trouve ou crée la cohorte de l'année suivante pour une mention donnée.
    Les redoublants rejoignent la MÊME cohorte que les nouveaux entrants.
    Convention : COH{MENTION}_{YEAR1}_{YEAR2}  (ex: COHINFO_2026_2027)
    """
    annee_suivante_num = int(annee_suivante.split('-')[0])
    annee_fin = annee_suivante_num + 1
    code = f"COH{mention_id}_{annee_suivante_num}_{annee_fin}"[:20]
    libelle = code

    cohorte, created = Cohorte.objects.get_or_create(
        code_cohorte=code,
        defaults={
            'lib_cohorte': libelle,
            'debut': date(annee_suivante_num, 10, 1),
            'code_mention_id': mention_id,
        }
    )
    if created:
        logger.info(f"Créé cohorte année suivante: {cohorte.code_cohorte} (mention={mention_id})")

    return cohorte


# ========== SCÉNARIO 2: COMPENSÉ - Créer InscriptionUE pour les dettes ==========

def _creer_inscriptions_ue_dettes(etudiant, dettes, classe_origine, annee_suivante):
    """
    Crée des InscriptionUE pour les dettes d'un étudiant compensé.
    L'étudiant passe en classe supérieure mais doit repasser ces cours
    auprès des enseignants de la classe d'origine.
    """
    count = 0
    for dette in dettes:
        InscriptionUE.objects.get_or_create(
            matricule_etudiant=etudiant,
            code_ue=dette.code_ue,
            code_ec=dette.code_ec,
            annee_academique=annee_suivante,
            code_classe=classe_origine,
            defaults={
                'type_inscription': 'DETTE_COMPENSEE'
            }
        )
        count += 1
    
    logger.info(f"Créé {count} InscriptionUE (dettes) pour {etudiant.matricule_et} (compensé)")
    return count


# ========== SCÉNARIO 3: DOUBLANT - Transférer Evaluation → Evaluation N+1 ==========

def _transferer_notes_doublant(etudiant, classe, annee_actuelle, annee_suivante):
    """
    Pour un étudiant doublant (ajourné/défaillant):
    - Copie les évaluations dont la note_finale >= 10 vers l'année suivante
    - Ne touche PAS aux évaluations déjà existantes en année N+1
      (si l'enseignant a déjà saisi des notes, elles sont préservées)
    """
    evaluations = Evaluation.objects.filter(
        matricule_etudiant=etudiant,
        code_classe=classe,
        annee_academique=annee_actuelle,
    ).select_related('code_ue', 'code_ec')

    count_transferees = 0
    for eval_obj in evaluations:
        if eval_obj.cc is None or eval_obj.examen is None:
            continue
        note_finale = float(eval_obj.cc) + float(eval_obj.examen)
        if eval_obj.rattrapage and float(eval_obj.rattrapage) > note_finale:
            note_finale = float(eval_obj.rattrapage)
        if eval_obj.rachat:
            note_finale = float(eval_obj.rachat)
        note_finale = round(note_finale, 1)

        # Transférer SEULEMENT les notes >= 10
        if note_finale >= 10:
            # get_or_create : ne PAS écraser si déjà existante en N+1
            _, created = Evaluation.objects.get_or_create(
                matricule_etudiant=etudiant,
                code_ue=eval_obj.code_ue,
                code_ec=eval_obj.code_ec,
                annee_academique=annee_suivante,
                code_classe=classe,
                defaults={
                    'cc': eval_obj.cc,
                    'examen': eval_obj.examen,
                    'rattrapage': eval_obj.rattrapage,
                    'rachat': eval_obj.rachat,
                }
            )
            if created:
                count_transferees += 1

    logger.info(f"Transféré {count_transferees} évaluations (note >= 10) pour {etudiant.matricule_et} (doublant)")
    return count_transferees


# ========== FONCTION UTILITAIRE: Récupérer les dettes pour le profil ==========

def recuperer_dettes_classe_inferieure(etudiant, classe_obj, annee_academique):
    """
    Récupère les dettes (InscriptionUE) d'un étudiant pour affichage informatif
    dans le profil/relevé de la classe supérieure.

    Les InscriptionUE sont créées avec code_classe = classe_inférieure (origine),
    donc on filtre uniquement par étudiant + année + type, sans filtrer par classe.
    Retourne les InscriptionUE de type DETTE_COMPENSEE et DETTE_LIQUIDEE pour l'année donnée.
    """
    dettes = InscriptionUE.objects.filter(
        matricule_etudiant=etudiant,
        annee_academique=annee_academique,
        type_inscription__in=['DETTE_COMPENSEE', 'DETTE_LIQUIDEE']
    ).select_related('code_ue', 'code_ec', 'code_classe')

    return list(dettes)


# ========== VUE PRINCIPALE ==========

@login_required
def passage_automatique_classe_superieure(request):
    """
    Vue principale pour le passage automatique des étudiants.
    
    Utilise decision_code (pas decision_label) pour le routage :
      SCÉNARIO 0 → Pré-vérif : L2 + dettes L1 non capitalisées → Redoublement (cohorte montante)
      SCÉNARIO 1 → ADM      → classe supérieure (ou diplôme)
      SCÉNARIO 2 → ADMD/COMP → classe supérieure + InscriptionUE (dettes)
      SCÉNARIO 3 → AJ/DEF   → Redoublement + notes >= 10 transférées
    """
    if request.user.role not in ['ADMIN', 'JURY']:
        messages.error(request, "Accès réservé aux administrateurs et jurys.")
        return redirect('jury_deliberer')
    
    # Récupérer les paramètres
    classe_code = request.GET.get('classe')
    annee_code = request.GET.get('annee')
    
    if not classe_code or not annee_code:
        messages.error(request, "Classe et année académique requises.")
        return redirect('jury_deliberer')
    
    try:
        classe = Classe.objects.get(code_classe=classe_code)
        annee_actuelle = AnneeAcademique.objects.get(code_anac=annee_code)
    except (Classe.DoesNotExist, AnneeAcademique.DoesNotExist):
        messages.error(request, "Classe ou année académique invalide.")
        return redirect('jury_deliberer')
    
    # Créer/récupérer l'année suivante
    try:
        annee_suivante_int = int(annee_code.split('-')[0]) + 1
        annee_suivante_code = f"{annee_suivante_int}-{annee_suivante_int + 1}"
        annee_suivante, created = AnneeAcademique.objects.get_or_create(
            code_anac=annee_suivante_code,
            defaults={'designation_anac': f"Année {annee_suivante_code}"}
        )
    except Exception as e:
        messages.error(request, f"Erreur lors de la création de l'année suivante: {str(e)}")
        return redirect('jury_deliberer')
    
    # ---- Garde contre la ré-exécution ----
    # Si des inscriptions existent déjà pour cette classe (ou supérieure) en année N+1,
    # on considère que le passage a déjà été effectué.
    classe_suivante_check = _get_classe_superieure(classe)
    deja_effectue = Inscription.objects.filter(
        annee_academique=annee_suivante_code,
        matricule_etudiant__inscription__code_classe=classe,
        matricule_etudiant__inscription__annee_academique=annee_code,
    ).exists()
    
    # Confirmation requise (GET = page de confirmation)
    if request.method != 'POST':
        inscriptions = Inscription.objects.filter(
            code_classe=classe,
            annee_academique=annee_code
        ).select_related('matricule_etudiant', 'cohorte')
        
        context = {
            'classe': classe,
            'classe_suivante': classe_suivante_check,
            'annee_actuelle': annee_actuelle,
            'annee_suivante': annee_suivante,
            'nb_etudiants': inscriptions.count(),
            'deja_effectue': deja_effectue,
        }
        return render(request, 'jury/passage_automatique_confirmation.html', context)
    
    # ---- Bloquer si déjà effectué ----
    if deja_effectue:
        messages.warning(request, 
            f"⚠️ Le passage automatique pour {classe.code_classe} ({annee_code} → {annee_suivante_code}) "
            f"a déjà été effectué. Des inscriptions N+1 existent déjà.")
        return redirect('jury_deliberer')
    
    # ================================================================
    # === TRAITEMENT DU PASSAGE AUTOMATIQUE (POST) ===
    # ================================================================
    
    inscriptions = Inscription.objects.filter(
        code_classe=classe,
        annee_academique=annee_code
    ).select_related('matricule_etudiant', 'cohorte')
    
    niveau_actuel = classe.code_niveau_id   # ex: 'L3', 'M2'
    mention = classe.code_mention_id         # ex: 'INFO'
    
    # Niveaux du cycle pour le calcul des crédits cumulés
    if niveau_actuel in ('L1', 'L2', 'L3'):
        niveaux_cycle = ['L1', 'L2', 'L3']
        seuil_diplome = SEUIL_LICENCE       # 180
    else:
        niveaux_cycle = ['M1', 'M2']
        seuil_diplome = SEUIL_MASTER        # 120
    
    est_fin_cycle = (niveau_actuel in ('L3', 'M2'))
    
    stats_globales = {
        'admis': 0,
        'compenses': 0,
        'doublants': 0,
        'bloques_dettes': 0,
        'diplomes_licence': 0,
        'diplomes_master': 0,
        'erreurs': 0,
        'ignores': 0,
    }
    
    stats_par_cohorte = {}
    logs = []
    
    for inscription in inscriptions:
        etudiant = inscription.matricule_etudiant
        cohorte = inscription.cohorte
        
        cohorte_code = cohorte.code_cohorte if cohorte else 'SANS_COHORTE'
        if cohorte_code not in stats_par_cohorte:
            stats_par_cohorte[cohorte_code] = {
                'admis': 0,
                'compenses': 0,
                'doublants': 0,
                'diplomes': 0,
                'dettes_total': 0
            }
        
        try:
            with transaction.atomic():
                from .views import _jury_compute_delib_ues
                
                stats_annuel = _jury_compute_delib_ues(classe, etudiant, 'annuel', None, annee_code)
                
                decision_code = stats_annuel.get('decision_code', 'ATT')
                decision_label = stats_annuel.get('decision_label', 'A déterminer')
                credits_annuel = stats_annuel.get('credits_valides', 0)
                dettes = _identifier_dettes_etudiant(etudiant, annee_code)
                nb_dettes = len(dettes)
                
                # Crédits cumulés (même mention, niveaux du cycle)
                credits_cumules = _calculer_credits_totaux_etudiant(etudiant, mention, niveaux_cycle)
                
                # Code inscription unique (matricule + année N+1)
                code_ins = f"INS-{etudiant.matricule_et}-{annee_suivante_code}"
                
                logger.debug(
                    f"Traitement: {etudiant.matricule_et} | "
                    f"Décision: {decision_label} ({decision_code}) | "
                    f"Crédits année: {credits_annuel} | "
                    f"Crédits cumulés ({'/'.join(niveaux_cycle)}): {credits_cumules} | "
                    f"Dettes: {nb_dettes}"
                )
                
                # === Marquer les dettes anciennement compensées qui sont maintenant capitalisées ===
                nb_liquidees = _marquer_dettes_liquidees(etudiant, mention)
                if nb_liquidees > 0:
                    logs.append(f"✅ {etudiant.nom_complet} - {nb_liquidees} dette(s) liquidée(s) (capitalisée(s))")
                
                # === SÉCURITÉ MASTER: pas de compensation en M1/M2 ===
                if niveau_actuel in ('M1', 'M2') and decision_code in ('ADMD', 'COMP'):
                    logger.warning(
                        f"⚠️ SÉCURITÉ: {etudiant.matricule_et} en {niveau_actuel} avec "
                        f"décision {decision_code} → forcé en AJ (pas de compensation en Master)"
                    )
                    decision_code = 'AJ'
                    decision_label = 'Ajourné (pas de compensation en Master)'
                
                # === Sauvegarder la décision annuelle sur l'inscription courante ===
                if decision_code in ('ADM', 'ADMD', 'COMP', 'AJ', 'DEF'):
                    inscription.decision_annuelle = decision_code
                    inscription.save(update_fields=['decision_annuelle'])
                
                # ============================================================
                # SCÉNARIO 0 (PRÉ-VÉRIFICATION): DETTES L1 NON CAPITALISÉES
                # Uniquement pour L2 → L3 : si l'étudiant a des dettes L1
                # non soldées, il redouble L2 (cohorte montante) même si
                # sa décision annuelle est ADM ou ADMD/COMP.
                # ============================================================
                dettes_L1_bloquantes = []
                if niveau_actuel == 'L2' and decision_code in ('ADM', 'ADMD', 'COMP'):
                    dettes_L1_bloquantes = _get_dettes_L1_non_capitalisees(etudiant, mention)
                
                if dettes_L1_bloquantes:
                    ue_dettes_str = ', '.join(
                        (d.code_ue.code_ue if d.code_ue else d.code_ec.code_ec)
                        for d in dettes_L1_bloquantes
                    )
                    logger.info(
                        f"🚫 BLOQUÉ DETTES L1: {etudiant.matricule_et} {decision_code} en L2 "
                        f"mais {len(dettes_L1_bloquantes)} dette(s) L1 non capitalisée(s): {ue_dettes_str}"
                    )
                    cohorte_montante = _trouver_cohorte_montante(classe, annee_code)
                    if cohorte_montante is None:
                        cohorte_montante = _trouver_ou_creer_cohorte_annee(mention, annee_suivante_code)
                    Inscription.objects.get_or_create(
                        code_inscription=code_ins,
                        defaults={
                            'matricule_etudiant': etudiant,
                            'code_classe': classe,
                            'annee_academique': annee_suivante_code,
                            'cohorte': cohorte_montante
                        }
                    )
                    _transferer_notes_doublant(etudiant, classe, annee_code, annee_suivante_code)
                    # Reporter les dettes L1 non capitalisées en N+1
                    for dette_nc in dettes_L1_bloquantes:
                        InscriptionUE.objects.get_or_create(
                            matricule_etudiant=etudiant,
                            code_ue=dette_nc.code_ue,
                            code_ec=dette_nc.code_ec,
                            annee_academique=annee_suivante_code,
                            code_classe=dette_nc.code_classe,
                            defaults={'type_inscription': 'DETTE_COMPENSEE'}
                        )
                    # Si ADMD/COMP cette année, reporter aussi les nouvelles dettes
                    if decision_code in ('ADMD', 'COMP'):
                        _creer_inscriptions_ue_dettes(etudiant, dettes, classe, annee_suivante_code)
                    stats_globales['bloques_dettes'] += 1
                    stats_par_cohorte[cohorte_code]['doublants'] += 1
                    logs.append(
                        f"🚫 {etudiant.nom_complet} - {decision_label} en L2 mais "
                        f"{len(dettes_L1_bloquantes)} dette(s) L1 non capitalisée(s) ({ue_dettes_str}) "
                        f"→ Redoublement (cohorte {cohorte_montante.code_cohorte})"
                    )
                
                # ============================================================
                # SCÉNARIO 1: ADMIS (ADM)
                # ============================================================
                elif decision_code == 'ADM':
                    
                    if est_fin_cycle and credits_cumules >= seuil_diplome:
                        # --- Diplômé ---
                        if niveau_actuel == 'L3':
                            # Licence → passage en M1
                            classe_suivante = _get_classe_superieure(classe)
                            if classe_suivante:
                                Inscription.objects.get_or_create(
                                    code_inscription=code_ins,
                                    defaults={
                                        'matricule_etudiant': etudiant,
                                        'code_classe': classe_suivante,
                                        'annee_academique': annee_suivante_code,
                                        'cohorte': cohorte
                                    }
                                )
                            stats_globales['diplomes_licence'] += 1
                            stats_par_cohorte[cohorte_code]['diplomes'] += 1
                            logs.append(f"✓ {etudiant.nom_complet} - Diplômé Licence ({credits_cumules} cr.) → {classe_suivante.code_classe if classe_suivante else 'FIN'}")
                        
                        else:  # M2
                            stats_globales['diplomes_master'] += 1
                            stats_par_cohorte[cohorte_code]['diplomes'] += 1
                            logs.append(f"✓ {etudiant.nom_complet} - Diplômé Master ({credits_cumules} cr.) - FIN DE PARCOURS")
                    
                    elif est_fin_cycle and credits_cumules < seuil_diplome:
                        # --- Fin de cycle mais crédits cumulés insuffisants → Redoublement ---
                        nouvelle_cohorte = _trouver_ou_creer_cohorte_annee(mention, annee_suivante_code)
                        Inscription.objects.get_or_create(
                            code_inscription=code_ins,
                            defaults={
                                'matricule_etudiant': etudiant,
                                'code_classe': classe,
                                'annee_academique': annee_suivante_code,
                                'cohorte': nouvelle_cohorte
                            }
                        )
                        _transferer_notes_doublant(etudiant, classe, annee_code, annee_suivante_code)
                        stats_globales['doublants'] += 1
                        stats_par_cohorte[cohorte_code]['doublants'] += 1
                        logs.append(f"⚠ {etudiant.nom_complet} - Admis année mais crédits cumulés insuffisants ({credits_cumules}/{seuil_diplome}) → Redoublement")
                    
                    else:
                        # --- Passage normal en classe supérieure ---
                        classe_suivante = _get_classe_superieure(classe)
                        if classe_suivante:
                            Inscription.objects.get_or_create(
                                code_inscription=code_ins,
                                defaults={
                                    'matricule_etudiant': etudiant,
                                    'code_classe': classe_suivante,
                                    'annee_academique': annee_suivante_code,
                                    'cohorte': cohorte
                                }
                            )
                            stats_globales['admis'] += 1
                            stats_par_cohorte[cohorte_code]['admis'] += 1
                            logs.append(f"✓ {etudiant.nom_complet} - Admis → {classe_suivante.code_classe}")
                        else:
                            stats_globales['erreurs'] += 1
                            logs.append(f"✗ {etudiant.nom_complet} - Admis mais pas de classe supérieure trouvée!")
                
                # ============================================================
                # SCÉNARIO 2: COMPENSÉ (ADMD ou COMP)
                # → Inscription classe supérieure + InscriptionUE (dettes)
                # ============================================================
                elif decision_code in ('ADMD', 'COMP'):
                    classe_suivante = _get_classe_superieure(classe)
                    
                    if classe_suivante:
                        logger.info(f"🔄 COMPENSÉ: {etudiant.matricule_et} → {classe_suivante.code_classe} + {nb_dettes} dettes")
                        
                        # 1. Inscription en classe supérieure
                        Inscription.objects.get_or_create(
                            code_inscription=code_ins,
                            defaults={
                                'matricule_etudiant': etudiant,
                                'code_classe': classe_suivante,
                                'annee_academique': annee_suivante_code,
                                'cohorte': cohorte
                            }
                        )
                        
                        # 2. Créer InscriptionUE pour chaque dette
                        _creer_inscriptions_ue_dettes(etudiant, dettes, classe, annee_suivante_code)
                        
                        stats_globales['compenses'] += 1
                        stats_par_cohorte[cohorte_code]['compenses'] += 1
                        stats_par_cohorte[cohorte_code]['dettes_total'] += nb_dettes
                        logs.append(f"✓ {etudiant.nom_complet} - Compensé ({nb_dettes} dettes) → {classe_suivante.code_classe}")
                    else:
                        logger.warning(f"⚠️ Pas de classe suivante pour {classe.code_classe} - compensé: {etudiant.nom_complet}")
                        logs.append(f"⚠ {etudiant.nom_complet} - Compensé mais pas de classe suivante!")
                
                # ============================================================
                # SCÉNARIO 3: AJOURNÉ (AJ) / DÉFAILLANT (DEF)
                # → Redoublement + notes >= 10 transférées
                # ============================================================
                elif decision_code in ('AJ', 'DEF'):
                    logger.info(f"↻ DOUBLANT: {etudiant.matricule_et} - {decision_label} ({decision_code})")
                    
                    # 1. Trouver/créer la cohorte N+1 (même promo que les nouveaux entrants)
                    nouvelle_cohorte = _trouver_ou_creer_cohorte_annee(mention, annee_suivante_code)
                    
                    # 2. Réinscription dans la même classe
                    Inscription.objects.get_or_create(
                        code_inscription=code_ins,
                        defaults={
                            'matricule_etudiant': etudiant,
                            'code_classe': classe,
                            'annee_academique': annee_suivante_code,
                            'cohorte': nouvelle_cohorte
                        }
                    )
                    
                    # 3. Transférer notes >= 10 (sans écraser celles existantes)
                    _transferer_notes_doublant(etudiant, classe, annee_code, annee_suivante_code)
                    
                    stats_globales['doublants'] += 1
                    stats_par_cohorte[cohorte_code]['doublants'] += 1
                    logs.append(f"↻ {etudiant.nom_complet} - {decision_label} ({decision_code}) → Redoublement {classe.code_classe}")
                
                else:
                    # Décision inconnue (ATT, NONE...) → ignoré
                    stats_globales['ignores'] += 1
                    logs.append(f"⚠ {etudiant.nom_complet} - Décision non traitée: {decision_label} ({decision_code})")
        
        except Exception as e:
            stats_globales['erreurs'] += 1
            logs.append(f"✗ {etudiant.nom_complet} - ERREUR: {str(e)}")
            logger.error(f"Erreur passage automatique pour {etudiant.matricule_et}: {str(e)}")
    
    # === MESSAGE RÉSUMÉ ===
    
    parts = [
        f"{'⚠️' if stats_globales['erreurs'] > 0 else '✅'} Passage automatique "
        f"{'terminé avec ' + str(stats_globales['erreurs']) + ' erreurs' if stats_globales['erreurs'] > 0 else 'terminé avec succès'} "
        f"pour {classe.code_classe} ({annee_code} → {annee_suivante_code}):",
        f"• {stats_globales['admis']} admis",
        f"• {stats_globales['compenses']} compensés (avec dettes InscriptionUE)",
        f"• {stats_globales['doublants']} doublants (notes >= 10 transférées)",
        f"• {stats_globales['bloques_dettes']} bloqués (dettes anciennes non capitalisées → redoublement)",
        f"• {stats_globales['diplomes_licence']} diplômés Licence",
        f"• {stats_globales['diplomes_master']} diplômés Master",
    ]
    if stats_globales['ignores'] > 0:
        parts.append(f"• {stats_globales['ignores']} ignorés (décision non déterminée)")
    
    resume = "\n        ".join(parts)
    
    if stats_globales['erreurs'] > 0:
        error_logs = [log for log in logs if log.startswith('✗')]
        resume += f"\n        Erreurs:\n        {chr(10).join(error_logs[:5])}"
        messages.error(request, resume)
        for error_log in error_logs:
            logger.error(error_log)
    else:
        messages.success(request, resume)
    
    # Logger les détails
    logger.info(f"Passage automatique {classe.code_classe}: {stats_globales}")
    for log in logs[:20]:
        logger.info(log)
    
    # Vérification finale
    classe_sup = _get_classe_superieure(classe)
    if classe_sup:
        inscriptions_suivante = Inscription.objects.filter(
            code_classe=classe_sup,
            annee_academique=annee_suivante_code
        ).count()
        logger.info(f"🔢 Vérification: {inscriptions_suivante} inscriptions en {classe_sup.code_classe} pour {annee_suivante_code}")
    
    inscriptions_ue_creees = InscriptionUE.objects.filter(
        annee_academique=annee_suivante_code,
        code_classe=classe
    ).count()
    logger.info(f"🔢 Vérification: {inscriptions_ue_creees} InscriptionUE (dettes) créées pour {annee_suivante_code}")
    
    return redirect('jury_deliberer')
