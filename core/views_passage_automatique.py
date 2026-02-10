"""
Vue pour le passage automatique des étudiants à la classe supérieure.
Architecture V2:
- ADMIS → Inscription classe supérieure
- COMPENSÉ → Inscription classe supérieure + InscriptionUE (dettes à reprendre)  
- AJOURNÉ/DÉFAILLANT → Redoublement même classe + Evaluation transférées (notes >= 10)
"""

import logging
import re
from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

from .models import Inscription, Deliberation, Evaluation, Etudiant, Cohorte, InscriptionUE
from reglage.models import Classe, AnneeAcademique

logger = logging.getLogger(__name__)


# ========== FONCTIONS UTILITAIRES ==========

def _get_classe_superieure(classe_actuelle):
    """
    Détermine la classe supérieure selon le niveau.
    Retourne None si l'étudiant est diplômé (M2).
    """
    code_classe = classe_actuelle.code_classe
    
    mapping = {
        'L1': 'L2',
        'L2': 'L3',
        'L3': 'M1',
        'M1': 'M2',
        'M2': None
    }
    
    for niveau, suivant in mapping.items():
        if niveau in code_classe:
            if suivant is None:
                return None
            try:
                code_suivant = code_classe.replace(niveau, suivant)
                return Classe.objects.get(code_classe=code_suivant)
            except Classe.DoesNotExist:
                logger.warning(f"Classe supérieure non trouvée pour {code_classe}")
                return None
    
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


def _calculer_credits_totaux_etudiant(etudiant, annee_academique):
    """
    Calcule le total des crédits capitalisés par un étudiant depuis le début de son parcours.
    Utilisé pour vérifier les conditions de diplôme (180 pour L3, 300 pour M2).
    """
    deliberations_validees = Deliberation.objects.filter(
        matricule_etudiant=etudiant,
        statut='VALIDE'
    ).select_related('code_ue', 'code_ec')
    
    credits_total = 0
    ues_comptees = set()
    
    for delib in deliberations_validees:
        if delib.code_ue and not delib.code_ec:
            ue_key = f"{delib.code_ue.code_ue}"
            if ue_key not in ues_comptees:
                credits_total += delib.code_ue.credit
                ues_comptees.add(ue_key)
        elif delib.code_ec:
            credits_total += delib.code_ec.credit
    
    return credits_total


def _creer_cohorte_redoublement(cohorte, annee_suivante):
    """
    Crée une nouvelle cohorte pour les redoublants basée sur la cohorte précédente.
    Retourne la nouvelle cohorte ou None.
    """
    if cohorte is None:
        return None
    
    annee_suivante_num = int(annee_suivante.split('-')[0])
    ancien_code = cohorte.code_cohorte
    ancien_libelle = cohorte.lib_cohorte or ancien_code
    
    annee_debut = annee_suivante.split('-')[0]
    annee_fin = annee_suivante.split('-')[1]
    
    # Pattern 1: Format XXXX_XXXX
    nouveau_code = re.sub(r'(\d{4})_(\d{4})', f'{annee_debut}_{annee_fin}', ancien_code)
    nouveau_libelle = re.sub(r'(\d{4})_(\d{4})', f'{annee_debut}_{annee_fin}', ancien_libelle)
    
    # Pattern 2: Format XXXX-XXXX
    if nouveau_code == ancien_code:
        nouveau_code = re.sub(r'\d{4}-\d{4}', annee_suivante, ancien_code)
        nouveau_libelle = re.sub(r'\d{4}-\d{4}', annee_suivante, ancien_libelle)
    
    # Pattern 3: Format XX_XX
    if nouveau_code == ancien_code:
        nouveau_code = re.sub(r'(\d{2})_(\d{2})', f'{annee_debut[2:]}_{annee_fin[2:]}', ancien_code)
        nouveau_libelle = re.sub(r'(\d{2})_(\d{2})', f'{annee_debut[2:]}_{annee_fin[2:]}', ancien_libelle)
    
    # Pattern 4: Format XX-XX
    if nouveau_code == ancien_code:
        nouveau_code = re.sub(r'\d{2}-\d{2}', f'{annee_debut[2:]}-{annee_fin[2:]}', ancien_code)
        nouveau_libelle = re.sub(r'\d{2}-\d{2}', f'{annee_debut[2:]}-{annee_fin[2:]}', ancien_libelle)
    
    # Fallback
    if nouveau_code == ancien_code:
        nouveau_code = f"{ancien_code}_{annee_debut[2:]}{annee_fin[2:]}"
        nouveau_libelle = f"{ancien_libelle} {annee_suivante}"
    
    nouveau_code = nouveau_code[:20]
    
    nouvelle_cohorte, created = Cohorte.objects.get_or_create(
        code_cohorte=nouveau_code,
        defaults={
            'lib_cohorte': nouveau_libelle[:100],
            'debut': date(annee_suivante_num, 10, 1)
        }
    )
    if created:
        logger.info(f"Créé nouvelle cohorte: {nouvelle_cohorte.code_cohorte} (basée sur {ancien_code})")
    
    return nouvelle_cohorte


# ========== SCÉNARIO 2: COMPENSÉ - Créer InscriptionUE pour les dettes ==========

def _creer_inscriptions_ue_dettes(etudiant, dettes, classe_origine, annee_suivante):
    """
    Crée des InscriptionUE pour les dettes d'un étudiant compensé.
    L'étudiant passe en classe supérieure mais doit repasser ces cours
    auprès des enseignants de la classe d'origine.
    
    Les enseignants verront ces étudiants via InscriptionUE quand ils
    ouvriront leur grille d'évaluation.
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


# ========== SCÉNARIO 3: DOUBLANT - Transférer Deliberation → Evaluation ==========

def _transferer_notes_doublant(etudiant, classe, annee_actuelle, annee_suivante):
    """
    Pour un étudiant doublant (ajourné/défaillant):
    - Copie les notes >= 10 (Deliberation → Evaluation) pour l'année suivante
    - Les notes < 10 ne sont PAS transférées (l'étudiant repart à zéro pour ces cours)
    - L'enseignant verra les notes pré-remplies et pourra les modifier
    """
    deliberations = Deliberation.objects.filter(
        matricule_etudiant=etudiant,
        code_classe=classe,
        annee_academique=annee_actuelle
    ).select_related('code_ue', 'code_ec')
    
    count_transferees = 0
    for delib in deliberations:
        note_finale = delib.calculer_note_finale()
        
        # Transférer SEULEMENT les notes >= 10 dans Evaluation pour l'année suivante
        if note_finale is not None and note_finale >= 10:
            Evaluation.objects.update_or_create(
                matricule_etudiant=etudiant,
                code_ue=delib.code_ue,
                code_ec=delib.code_ec,
                annee_academique=annee_suivante,
                code_classe=classe,
                defaults={
                    'cc': delib.cc,
                    'examen': delib.examen,
                    'rattrapage': delib.rattrapage,
                    'rachat': delib.rachat,
                }
            )
            count_transferees += 1
    
    logger.info(f"Transféré {count_transferees} évaluations (notes >= 10) pour {etudiant.matricule_et} (doublant)")
    return count_transferees


# ========== FONCTION UTILITAIRE: Récupérer les dettes pour le profil ==========

def recuperer_dettes_classe_inferieure(etudiant, classe_obj, annee_academique):
    """
    Récupère les dettes (InscriptionUE) d'un étudiant pour affichage informatif
    dans le profil/relevé de la classe supérieure.
    
    Retourne les InscriptionUE de type DETTE_COMPENSEE pour l'année donnée.
    """
    dettes = InscriptionUE.objects.filter(
        matricule_etudiant=etudiant,
        annee_academique=annee_academique,
        type_inscription='DETTE_COMPENSEE'
    ).select_related('code_ue', 'code_ec', 'code_classe')
    
    return list(dettes)


# ========== VUE PRINCIPALE ==========

@login_required
def passage_automatique_classe_superieure(request):
    """
    Vue principale pour le passage automatique des étudiants à la classe supérieure.
    
    3 scénarios:
    - ADMIS → Inscription classe supérieure (simple)
    - COMPENSÉ → Inscription classe supérieure + InscriptionUE (dettes à reprendre)
    - AJOURNÉ/DÉFAILLANT → Redoublement même classe + Evaluation transférées (notes >= 10)
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
    
    # Confirmation requise (GET = page de confirmation)
    if request.method != 'POST':
        inscriptions = Inscription.objects.filter(
            code_classe=classe,
            annee_academique=annee_code
        ).select_related('matricule_etudiant', 'cohorte')
        
        classe_suivante = _get_classe_superieure(classe)
        
        context = {
            'classe': classe,
            'classe_suivante': classe_suivante,
            'annee_actuelle': annee_actuelle,
            'annee_suivante': annee_suivante,
            'nb_etudiants': inscriptions.count(),
        }
        return render(request, 'jury/passage_automatique_confirmation.html', context)
    
    # ================================================================
    # === TRAITEMENT DU PASSAGE AUTOMATIQUE (POST) ===
    # ================================================================
    
    inscriptions = Inscription.objects.filter(
        code_classe=classe,
        annee_academique=annee_code
    ).select_related('matricule_etudiant', 'cohorte')
    
    stats_globales = {
        'admis': 0,
        'compenses': 0,
        'doublants': 0,
        'diplomes_licence': 0,
        'diplomes_master': 0,
        'erreurs': 0
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
                
                decision = stats_annuel.get('decision_label', 'A déterminer')
                credits_annuel = stats_annuel.get('credits_valides', 0)
                credits_totaux = _calculer_credits_totaux_etudiant(etudiant, annee_code)
                dettes = _identifier_dettes_etudiant(etudiant, annee_code)
                nb_dettes = len(dettes)
                
                logger.debug(f"Traitement: {etudiant.matricule_et} | Décision: {decision} | Crédits: {credits_annuel}/{credits_totaux} | Dettes: {nb_dettes}")
                
                # ============================================================
                # SCÉNARIO 1: ADMIS
                # ============================================================
                if decision == 'Admis':
                    
                    # === Diplômé Licence (L3 + 180 crédits) → Passage en M1 ===
                    if 'L3' in classe.code_classe and credits_totaux == 180:
                        classe_suivante = _get_classe_superieure(classe)
                        if classe_suivante:
                            Inscription.objects.get_or_create(
                                code_inscription=f"INS-{etudiant.matricule_et}-{annee_suivante_code}",
                                defaults={
                                    'matricule_etudiant': etudiant,
                                    'code_classe': classe_suivante,
                                    'annee_academique': annee_suivante_code,
                                    'cohorte': cohorte
                                }
                            )
                            stats_globales['diplomes_licence'] += 1
                            stats_par_cohorte[cohorte_code]['diplomes'] += 1
                            logs.append(f"✓ {etudiant.nom_complet} - Diplômé Licence (180 crédits) → {classe_suivante.code_classe}")
                    
                    # === Diplômé Master (M2 + 300 crédits) → Fin de parcours ===
                    elif 'M2' in classe.code_classe and credits_totaux == 300:
                        stats_globales['diplomes_master'] += 1
                        stats_par_cohorte[cohorte_code]['diplomes'] += 1
                        logs.append(f"✓ {etudiant.nom_complet} - Diplômé Master (300 crédits) - FIN DE PARCOURS")
                    
                    # === L3/M2 Admis mais crédits insuffisants → Redoublement ===
                    elif ('L3' in classe.code_classe and credits_totaux != 180) or \
                         ('M2' in classe.code_classe and credits_totaux != 300):
                        # Redoublement: réinscription même classe
                        nouvelle_cohorte = _creer_cohorte_redoublement(cohorte, annee_suivante_code)
                        Inscription.objects.get_or_create(
                            code_inscription=f"INS-{etudiant.matricule_et}-{annee_suivante_code}",
                            defaults={
                                'matricule_etudiant': etudiant,
                                'code_classe': classe,
                                'annee_academique': annee_suivante_code,
                                'cohorte': nouvelle_cohorte
                            }
                        )
                        # Transférer notes >= 10 dans Evaluation année N+1
                        _transferer_notes_doublant(etudiant, classe, annee_code, annee_suivante_code)
                        stats_globales['doublants'] += 1
                        stats_par_cohorte[cohorte_code]['doublants'] += 1
                        logs.append(f"⚠ {etudiant.nom_complet} - Admis mais crédits insuffisants ({credits_totaux}) → Redoublement")
                    
                    # === Passage normal en classe supérieure ===
                    else:
                        classe_suivante = _get_classe_superieure(classe)
                        if classe_suivante:
                            Inscription.objects.get_or_create(
                                code_inscription=f"INS-{etudiant.matricule_et}-{annee_suivante_code}",
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
                
                # ============================================================
                # SCÉNARIO 2: COMPENSÉ (Admis avec dette)
                # → Inscription classe supérieure
                # → InscriptionUE pour les dettes (enseignants classe origine les verront)
                # ============================================================
                elif decision == 'Admis avec dette':
                    classe_suivante = _get_classe_superieure(classe)
                    
                    if classe_suivante:
                        logger.info(f"🔄 COMPENSÉ: {etudiant.matricule_et} → {classe_suivante.code_classe} + {nb_dettes} dettes")
                        
                        # 1. Inscription en classe supérieure
                        Inscription.objects.get_or_create(
                            code_inscription=f"INS-{etudiant.matricule_et}-{annee_suivante_code}",
                            defaults={
                                'matricule_etudiant': etudiant,
                                'code_classe': classe_suivante,
                                'annee_academique': annee_suivante_code,
                                'cohorte': cohorte
                            }
                        )
                        
                        # 2. Créer InscriptionUE pour chaque dette
                        #    Les enseignants de la classe d'origine verront ces étudiants
                        _creer_inscriptions_ue_dettes(etudiant, dettes, classe, annee_suivante_code)
                        
                        stats_globales['compenses'] += 1
                        stats_par_cohorte[cohorte_code]['compenses'] += 1
                        stats_par_cohorte[cohorte_code]['dettes_total'] += nb_dettes
                        logs.append(f"✓ {etudiant.nom_complet} - Compensé ({nb_dettes} dettes) → {classe_suivante.code_classe}")
                    else:
                        logger.warning(f"⚠️ Pas de classe suivante pour {classe.code_classe} - compensé: {etudiant.nom_complet}")
                        logs.append(f"⚠ {etudiant.nom_complet} - Compensé mais pas de classe suivante!")
                
                # ============================================================
                # SCÉNARIO 3: AJOURNÉ / DÉFAILLANT
                # → Redoublement même classe
                # → Copier notes >= 10 (Deliberation → Evaluation année N+1)
                # → Nouvelle cohorte auto-créée
                # ============================================================
                else:
                    logger.info(f"↻ DOUBLANT: {etudiant.matricule_et} - {decision}")
                    
                    # 1. Créer nouvelle cohorte pour le redoublement
                    nouvelle_cohorte = _creer_cohorte_redoublement(cohorte, annee_suivante_code)
                    
                    # 2. Réinscription dans la même classe pour l'année suivante
                    Inscription.objects.get_or_create(
                        code_inscription=f"INS-{etudiant.matricule_et}-{annee_suivante_code}",
                        defaults={
                            'matricule_etudiant': etudiant,
                            'code_classe': classe,
                            'annee_academique': annee_suivante_code,
                            'cohorte': nouvelle_cohorte
                        }
                    )
                    
                    # 3. Transférer notes >= 10 dans Evaluation année N+1
                    #    Les notes < 10 ne sont PAS transférées (l'étudiant repart à zéro)
                    #    Les enseignants verront les notes pré-remplies et pourront les modifier
                    _transferer_notes_doublant(etudiant, classe, annee_code, annee_suivante_code)
                    
                    stats_globales['doublants'] += 1
                    stats_par_cohorte[cohorte_code]['doublants'] += 1
                    logs.append(f"↻ {etudiant.nom_complet} - {decision} → Redoublement {classe.code_classe}")
        
        except Exception as e:
            stats_globales['erreurs'] += 1
            logs.append(f"✗ {etudiant.nom_complet} - ERREUR: {str(e)}")
            logger.error(f"Erreur passage automatique pour {etudiant.matricule_et}: {str(e)}")
    
    # === MESSAGE RÉSUMÉ ===
    
    resume = f"""
        {'⚠️' if stats_globales['erreurs'] > 0 else '✅'} Passage automatique {'terminé avec ' + str(stats_globales['erreurs']) + ' erreurs' if stats_globales['erreurs'] > 0 else 'terminé avec succès'} pour {classe.code_classe} ({annee_code} → {annee_suivante_code}):
        • {stats_globales['admis']} admis
        • {stats_globales['compenses']} compensés (avec dettes InscriptionUE)
        • {stats_globales['doublants']} doublants (notes >= 10 transférées en Evaluation)
        • {stats_globales['diplomes_licence']} diplômés Licence
        • {stats_globales['diplomes_master']} diplômés Master
    """
    
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
