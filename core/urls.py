from django.urls import path
from . import views
from . import views_jury_presence
from . import views_passage_automatique

urlpatterns = [
    # Accueil et authentification
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('modifier-photo/', views.modifier_ma_photo, name='modifier_ma_photo'),
    path('changer-mot-de-passe/', views.change_password, name='change_password'),
    
    # URLs Étudiant
    path('etudiant/', views.etudiant_dashboard, name='etudiant_dashboard'),
    path('etudiant/profil/', views.etudiant_profil, name='etudiant_profil'),
    path('etudiant/notes/', views.etudiant_notes, name='etudiant_notes'),
    path('etudiant/envoyer-recours/', views.envoyer_recours, name='envoyer_recours'),
    path('etudiant/mes-cours/', views.etudiant_mes_cours, name='etudiant_mes_cours'),
    path('etudiant/communique/', views.etudiant_communique, name='etudiant_communique'),
    path('etudiant/commentaires/', views.etudiant_commentaires, name='etudiant_commentaires'),
    path('etudiant/evaluer-enseignant/', views.etudiant_evaluer_enseignant, name='etudiant_evaluer_enseignant'),
    path('etudiant/resultats/', views.etudiant_resultats, name='etudiant_resultats'),
    path('etudiant/telecharger-bulletin/', views.etudiant_telecharger_bulletin, name='etudiant_telecharger_bulletin'),
    path('etudiant/bulletin-pdf/', views.etudiant_bulletin_pdf, name='etudiant_bulletin_pdf'),
    
    # URLs Enseignant
    path('enseignant/', views.enseignant_dashboard, name='enseignant_dashboard'),
    path('enseignant/profil/', views.enseignant_profil, name='enseignant_profil'),
    path('enseignant/mes-cours/', views.enseignant_mes_cours, name='enseignant_mes_cours'),
    path('enseignant/commentaires/', views.enseignant_commentaires, name='enseignant_commentaires'),
    path('enseignant/appreciations/', views.enseignant_appreciations, name='enseignant_appreciations'),
    path('enseignant/evaluations/', views.enseignant_evaluations, name='enseignant_evaluations'),
    path('enseignant/encoder/', views.enseignant_encoder_notes, name='enseignant_encoder_notes'),
    path('enseignant/notifications/', views.enseignant_notifications, name='enseignant_notifications'),
    path('enseignant/evaluer/<str:code_cours>/<str:annee>/', views.enseignant_evaluer_cours, name='enseignant_evaluer_cours'),
    path('enseignant/evaluer/<str:code_cours>/<str:annee>/telecharger/', views.telecharger_grille_evaluation, name='telecharger_grille_evaluation'),
    path('enseignant/evaluer/<str:code_cours>/<str:annee>/importer/', views.importer_grille_evaluation, name='importer_grille_evaluation'),
    path('enseignant/evaluer/<str:code_cours>/<str:annee>/envoyer-jury/', views.envoyer_au_jury, name='envoyer_au_jury'),
    
    # URLs Admin Simulation
    path('simulate/etudiant/<str:matricule>/', views.admin_simulate_etudiant, name='admin_simulate_etudiant'),
    path('simulate/enseignant/<str:matricule>/', views.admin_simulate_enseignant, name='admin_simulate_enseignant'),
    path('simulate/jury/<str:code_jury>/', views.admin_simulate_jury, name='admin_simulate_jury'),
    path('simulate/stop/', views.admin_stop_simulation, name='admin_stop_simulation'),
    
    # URLs Jury
    path('jury/', views.jury_dashboard, name='jury_dashboard'),
    path('jury/grille-cours/', views.jury_grille_cours, name='jury_grille_cours'),
    path('jury/evaluations/', views.jury_evaluations, name='jury_evaluations'),
    path('jury/evaluations/action/', views.jury_evaluations_action, name='jury_evaluations_action'),
    path('jury/evaluations/<int:eval_id>/edit/', views.jury_evaluation_edit, name='jury_evaluation_edit'),
    path('jury/evaluations/<int:eval_id>/delete/', views.jury_evaluation_delete, name='jury_evaluation_delete'),
    path('jury/evaluer/<str:code_cours>/<str:annee>/', views.jury_evaluer_cours, name='jury_evaluer_cours'),
    path('jury/toggle-parametre/', views.jury_toggle_parametre, name='jury_toggle_parametre'),
    path('jury/deliberer/', views.jury_deliberer, name='jury_deliberer'),
    path('jury/deliberer/annuler/', views.jury_annuler_deliberation, name='jury_annuler_deliberation'),
    path('jury/deliberations/', views.jury_deliberations, name='jury_deliberations'),
    path('jury/deliberations/action/', views.jury_deliberations_action, name='jury_deliberations_action'),
    path('jury/deliberations/<int:delib_id>/edit/', views.jury_deliberation_edit, name='jury_deliberation_edit'),
    path('jury/deliberations/<int:delib_id>/delete/', views.jury_deliberation_delete, name='jury_deliberation_delete'),
    path('jury/publier/', views.jury_publier, name='jury_publier'),
    path('jury/communique/', views.jury_communique, name='jury_communique'),
    path('jury/imprimables/', views.jury_imprimables, name='jury_imprimables'),
    path('jury/imprimables/palmares/', views.jury_imprimable_palmare, name='jury_imprimable_palmare'),
    path('jury/imprimables/pv/', views.jury_imprimable_pv, name='jury_imprimable_pv'),
    path('jury/imprimables/releves/', views.jury_imprimable_releves, name='jury_imprimable_releves'),
    path('jury/imprimables/releves/<str:matricule>/', views.jury_imprimable_releve, name='jury_imprimable_releve'),
    path('jury/imprimables/profil/<str:matricule>/', views.jury_imprimable_profil, name='jury_imprimable_profil'),
    path('jury/imprimables/profil-pdf/<str:matricule>/', views.jury_imprimable_profil_pdf, name='jury_imprimable_profil_pdf'),
    path('jury/imprimables/releves-tous/', views.jury_imprimable_releves_tous, name='jury_imprimable_releves_tous'),
    path('jury/imprimables/profils-tous/', views.jury_imprimable_profils_tous, name='jury_imprimable_profils_tous'),
    path('jury/imprimables/releves-selectionnes/', views_jury_presence.jury_imprimable_releves_selectionnes, name='jury_imprimable_releves_selectionnes'),
    path('jury/imprimables/profils-selectionnes/', views_jury_presence.jury_imprimable_profils_selectionnes, name='jury_imprimable_profils_selectionnes'),
    path('jury/presence-deliberation/', views.jury_presence_deliberation, name='jury_presence_deliberation'),
    path('jury/cohorte/', views.jury_cohorte, name='jury_cohorte'),
    path('jury/recours/', views.jury_recours, name='jury_recours'),
    path('jury/recours/<str:code_recours>/', views.jury_detail_recours, name='jury_detail_recours'),
    path('jury/recours/<str:code_recours>/traiter/', views.jury_traiter_recours, name='jury_traiter_recours'),
    path('jury/recours/<str:code_recours>/modifier/', views.jury_modifier_recours, name='jury_modifier_recours'),
    path('jury/recours/<str:code_recours>/supprimer/', views.jury_supprimer_recours, name='jury_supprimer_recours'),
    path('jury/recours-pdf/', views.jury_recours_pdf, name='jury_recours_pdf'),
    path('jury/passage-automatique/', views_passage_automatique.passage_automatique_classe_superieure, name='passage_automatique_classe_superieure'),
    
    # URLs Gestion Admin
    path('gestion/utilisateurs/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('gestion/utilisateurs/modifier/<int:user_id>/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('gestion/utilisateurs/supprimer/<int:user_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('gestion/utilisateurs/reinitialiser/<int:user_id>/', views.reinitialiser_mot_de_passe, name='reinitialiser_mot_de_passe'),
    path('gestion/utilisateurs/supprimer-selection/', views.supprimer_utilisateurs_selection, name='supprimer_utilisateurs_selection'),
    path('gestion/utilisateurs/exporter-credentials/', views.exporter_credentials_utilisateurs, name='exporter_credentials_utilisateurs'),
    path('gestion/etudiants/', views.gestion_etudiants, name='gestion_etudiants'),
    path('gestion/etudiants/reinitialiser-mots-de-passe/', views.reinitialiser_mdp_tous_etudiants, name='reinitialiser_mdp_tous_etudiants'),
    path('gestion/enseignants/', views.gestion_enseignants, name='gestion_enseignants'),
    path('gestion/enseignants/generer-comptes/', views.generer_comptes_enseignants_existants, name='generer_comptes_enseignants_existants'),
    path('gestion/ue/', views.gestion_ue, name='gestion_ue'),
    path('gestion/ec/', views.gestion_ec, name='gestion_ec'),
    path('gestion/jurys/', views.gestion_jurys, name='gestion_jurys'),
    path('gestion/cohortes/', views.gestion_cohortes, name='gestion_cohortes'),
    path('gestion/inscriptions/', views.gestion_inscriptions, name='gestion_inscriptions'),
    path('statistiques/', views.statistiques, name='statistiques'),
    path('historique/', views.historique_actions, name='historique_actions'),
    
    # URLs Actions Étudiants
    path('gestion/etudiants/modifier/<str:matricule>/', views.modifier_etudiant, name='modifier_etudiant'),
    path('gestion/etudiants/supprimer/<str:matricule>/', views.supprimer_etudiant, name='supprimer_etudiant'),
    path('gestion/etudiants/voir/<str:matricule>/', views.voir_etudiant, name='voir_etudiant'),
    
    # URLs Actions Enseignants
    path('gestion/enseignants/voir/<str:matricule>/', views.voir_enseignant, name='voir_enseignant'),
    path('gestion/enseignants/modifier/<str:matricule>/', views.modifier_enseignant, name='modifier_enseignant'),
    path('gestion/enseignants/supprimer/<str:matricule>/', views.supprimer_enseignant, name='supprimer_enseignant'),
    
    # URLs Actions UE
    path('gestion/ue/modifier/<str:code>/', views.modifier_ue, name='modifier_ue'),
    path('gestion/ue/supprimer/<str:code>/', views.supprimer_ue, name='supprimer_ue'),
    
    # URLs Actions EC
    path('gestion/ec/modifier/<str:code>/', views.modifier_ec, name='modifier_ec'),
    path('gestion/ec/supprimer/<str:code>/', views.supprimer_ec, name='supprimer_ec'),
    
    # URLs Actions Jurys
    path('gestion/jurys/modifier/<str:code>/', views.modifier_jury, name='modifier_jury'),
    path('gestion/jurys/supprimer/<str:code>/', views.supprimer_jury, name='supprimer_jury'),
    
    # URLs Actions Cohortes
    path('gestion/cohortes/modifier/<str:code>/', views.modifier_cohorte, name='modifier_cohorte'),
    path('gestion/cohortes/supprimer/<str:code>/', views.supprimer_cohorte, name='supprimer_cohorte'),
    path('gestion/cohortes/voir/<str:code>/', views.voir_cohorte, name='voir_cohorte'),
    
    # URLs Actions Inscriptions
    path('gestion/inscriptions/modifier/<str:code>/', views.modifier_inscription, name='modifier_inscription'),
    path('gestion/inscriptions/supprimer/<str:code>/', views.supprimer_inscription, name='supprimer_inscription'),
    path('gestion/inscriptions/voir/<str:code>/', views.voir_inscription, name='voir_inscription'),
    
    # URLs Attributions et Réglage
    path('gestion/attributions/', views.gestion_attributions, name='gestion_attributions'),
    path('gestion/attributions/liste/', views.liste_attributions, name='liste_attributions'),
    path('gestion/attributions/import/', views.import_attributions, name='import_attributions'),
    path('gestion/attributions/supprimer-tout/', views.supprimer_tout_attributions, name='supprimer_tout_attributions'),
    path('gestion/attributions/supprimer/<str:code>/', views.supprimer_attribution, name='supprimer_attribution'),
    path('gestion/attributions/modifier/<str:code>/', views.modifier_attribution, name='modifier_attribution'),
    path('gestion/attributions/ajouter-cours/', views.ajouter_cours_attribution, name='ajouter_cours_attribution'),
    path('gestion/attributions/supprimer-cours/', views.supprimer_cours_attribution, name='supprimer_cours_attribution'),
    path('gestion/attributions/vider/', views.vider_cours_attribution, name='vider_cours_attribution'),
    path('gestion/attributions/attribuer/', views.attribuer_cours, name='attribuer_cours'),
    path('gestion/attributions/migrer/', views.migrer_ue_ec, name='migrer_ue_ec'),
    path('gestion/reglage/', views.gestion_reglage, name='gestion_reglage'),
    
    # URLs AJAX
    path('gestion/ajax/get-section-for-departement/', views.get_section_for_departement, name='get_section_for_departement'),

    # URLs Importation Excel
    path('gestion/etudiants/import/', views.import_etudiants, name='import_etudiants'),
    path('gestion/enseignants/import/', views.import_enseignants, name='import_enseignants'),
    path('gestion/enseignants/import/ajax/', views.import_enseignants_ajax, name='import_enseignants_ajax'),
    path('gestion/etudiants/import/ajax/', views.import_etudiants_ajax, name='import_etudiants_ajax'),
    path('gestion/ue/import/', views.import_ue, name='import_ue'),
    path('gestion/ue/import/ajax/', views.import_ue_ajax, name='import_ue_ajax'),
    path('gestion/ec/import/', views.import_ec, name='import_ec'),
    path('gestion/ec/import/ajax/', views.import_ec_ajax, name='import_ec_ajax'),
    path('gestion/inscriptions/import/', views.import_inscriptions, name='import_inscriptions'),
    path('gestion/inscriptions/import/ajax/', views.import_inscriptions_ajax, name='import_inscriptions_ajax'),
    path('gestion/cohortes/import/', views.import_cohortes, name='import_cohortes'),
    path('gestion/cohortes/import/ajax/', views.import_cohortes_ajax, name='import_cohortes_ajax'),
    path('gestion/attributions/import/ajax/', views.import_attributions_ajax, name='import_attributions_ajax'),
    path('gestion/modele-excel/<str:model_type>/', views.telecharger_modele_excel, name='telecharger_modele_excel'),
    
    # URLs Suppression en masse
    path('gestion/ue/supprimer-tout/', views.supprimer_tout_ue, name='supprimer_tout_ue'),
    path('gestion/ec/supprimer-tout/', views.supprimer_tout_ec, name='supprimer_tout_ec'),
    path('gestion/etudiants/supprimer-tout/', views.supprimer_tout_etudiants, name='supprimer_tout_etudiants'),
    path('gestion/enseignants/supprimer-tout/', views.supprimer_tout_enseignants, name='supprimer_tout_enseignants'),
    path('gestion/inscriptions/supprimer-tout/', views.supprimer_tout_inscriptions, name='supprimer_tout_inscriptions'),
    
    # URLs Gestionnaire - Rapports et visualisation
    path('gestionnaire/communiques-jury/', views.gestionnaire_communiques_jury, name='gestionnaire_communiques_jury'),
    path('gestionnaire/deliberations/', views.gestionnaire_deliberations, name='gestionnaire_deliberations'),
    path('gestionnaire/evaluations/', views.gestionnaire_evaluations, name='gestionnaire_evaluations'),
    path('gestionnaire/commentaires-etudiants/', views.gestionnaire_commentaires_etudiants, name='gestionnaire_commentaires_etudiants'),
    path('gestionnaire/commentaires-enseignants/', views.gestionnaire_commentaires_enseignants, name='gestionnaire_commentaires_enseignants'),
    
    # URLs Gestionnaire - Imports
    path('gestionnaire/import/attributions/', views.gestionnaire_import_attributions, name='gestionnaire_import_attributions'),
    path('gestionnaire/download/template-attributions/', views.telecharger_template_attributions, name='telecharger_template_attributions'),
]
