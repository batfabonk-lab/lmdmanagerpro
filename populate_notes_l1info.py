#!/usr/bin/env python
"""
Script de peuplement des notes pour les étudiants L1INFO - Semestre 1
"""

import os
import sys
import django
import random

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from core.models import Etudiant, UE, EC, Evaluation, Inscription, Classe
from reglage.models import AnneeAcademique
from django.db import transaction

def generer_notes_l1info_s1():
    """Génère des notes CC et Examen pour tous les cours S1 des étudiants L1INFO"""
    
    print("Generation des notes pour les étudiants L1INFO - Semestre 1...")
    
    # Récupérer la classe L1INFO
    try:
        classe_l1info = Classe.objects.get(code_classe='L1INFO')
        print(f"Classe trouvée: {classe_l1info}")
    except Classe.DoesNotExist:
        print("Erreur: Classe L1INFO non trouvée!")
        return
    
    # Récupérer l'année académique active
    annee_active = AnneeAcademique.objects.filter(active=True).first()
    if not annee_active:
        annee_active = AnneeAcademique.objects.first()
    
    print(f"Année académique: {annee_active}")
    
    # Récupérer les étudiants inscrits en L1INFO
    etudiants_l1info = Etudiant.objects.filter(
        inscription__code_classe=classe_l1info,
        inscription__annee_academique=annee_active.code_anac
    ).distinct()
    
    print(f"Nombre d'étudiants L1INFO trouvés: {etudiants_l1info.count()}")
    
    if etudiants_l1info.count() == 0:
        print("Aucun étudiant trouvé en L1INFO!")
        return
    
    # Récupérer tous les UE et EC du semestre 1
    ues_s1 = UE.objects.filter(semestre=1)
    ecs_s1 = EC.objects.filter(code_ue__semestre=1)
    
    print(f"Nombre d'UEs S1: {ues_s1.count()}")
    print(f"Nombre d'ECs S1: {ecs_s1.count()}")
    
    if ues_s1.count() == 0 and ecs_s1.count() == 0:
        print("Aucun cours trouvé pour le semestre 1!")
        return
    
    # Statistiques
    total_evaluations = 0
    total_etudiants = etudiants_l1info.count()
    total_cours = ues_s1.count() + ecs_s1.count()
    
    print(f"\nGeneration des notes...")
    print(f"   - Étudiants: {total_etudiants}")
    print(f"   - Cours: {total_cours}")
    print(f"   - Évaluations à créer: {total_etudiants * total_cours}")
    
    # Génération des notes avec transaction
    with transaction.atomic():
        for etudiant in etudiants_l1info:
            print(f"\nEtudiant: {etudiant.nom_complet} ({etudiant.matricule_et})")
            
            # Générer les notes pour les UE
            for ue in ues_s1:
                # Vérifier si l'UE a des EC
                ecs_de_lue = EC.objects.filter(code_ue=ue)
                
                if ecs_de_lue.exists():
                    # L'UE a des EC, on ne la note pas directement
                    print(f"   UE {ue.code_ue}: a des EC, pas de note directe")
                    # Supprimer l'évaluation de l'UE si elle existe
                    Evaluation.objects.filter(
                        matricule_etudiant=etudiant,
                        code_ue=ue,
                        code_ec=None
                    ).delete()
                else:
                    # L'UE n'a pas d'EC, on peut la noter
                    # Vérifier si l'évaluation existe déjà
                    evaluation, created = Evaluation.objects.get_or_create(
                        matricule_etudiant=etudiant,
                        code_ue=ue,
                        code_ec=None,
                        defaults={
                            'cc': None,
                            'examen': None,
                            'statut': 'EN_COURS'
                        }
                    )
                    
                    if created or evaluation.cc is None:
                        # Générer des notes aléatoires réalistes (sur 10)
                        cc = round(random.uniform(4, 9), 1)  # CC sur 10
                        examen = round(random.uniform(3, 9.5), 1)  # Examen sur 10
                        
                        evaluation.cc = cc
                        evaluation.examen = examen
                        
                        # Calculer la note finale pour déterminer le statut
                        note_finale = evaluation.calculer_note_finale()
                        if note_finale >= 10:
                            evaluation.statut = 'VALIDE'
                        else:
                            evaluation.statut = 'NON_VALIDE'
                        
                        evaluation.save()
                        print(f"   UE {ue.code_ue}: CC={cc}/10, Examen={examen}/10, Final={note_finale}/20 ({evaluation.statut})")
                        total_evaluations += 1
                    else:
                        # Mettre à jour les notes existantes pour être sur 10
                        cc = round(random.uniform(4, 9), 1)  # CC sur 10
                        examen = round(random.uniform(3, 9.5), 1)  # Examen sur 10
                        
                        evaluation.cc = cc
                        evaluation.examen = examen
                        
                        # Calculer la note finale pour déterminer le statut
                        note_finale = evaluation.calculer_note_finale()
                        if note_finale >= 10:
                            evaluation.statut = 'VALIDE'
                        else:
                            evaluation.statut = 'NON_VALIDE'
                        
                        evaluation.save()
                        print(f"   UE {ue.code_ue}: CC={cc}/10, Examen={examen}/10, Final={note_finale}/20 ({evaluation.statut}) [MIS À JOUR]")
                        total_evaluations += 1
            
            # Générer les notes pour les EC
            for ec in ecs_s1:
                # Vérifier si l'évaluation existe déjà
                evaluation, created = Evaluation.objects.get_or_create(
                    matricule_etudiant=etudiant,
                    code_ue=None,
                    code_ec=ec,
                    defaults={
                        'cc': None,
                        'examen': None,
                        'statut': 'EN_COURS'
                    }
                )
                
                if created or evaluation.cc is None:
                    # Générer des notes aléatoires réalistes (sur 10)
                    cc = round(random.uniform(4, 9), 1)  # CC sur 10
                    examen = round(random.uniform(3, 9.5), 1)  # Examen sur 10
                    
                    evaluation.cc = cc
                    evaluation.examen = examen
                    
                    # Calculer la note finale pour déterminer le statut
                    note_finale = evaluation.calculer_note_finale()
                    if note_finale >= 10:
                        evaluation.statut = 'VALIDE'
                    else:
                        evaluation.statut = 'NON_VALIDE'
                    
                    evaluation.save()
                    print(f"   EC {ec.code_ec}: CC={cc}/10, Examen={examen}/10, Final={note_finale}/20 ({evaluation.statut})")
                    total_evaluations += 1
                else:
                    # Mettre à jour les notes existantes pour être sur 10
                    cc = round(random.uniform(4, 9), 1)  # CC sur 10
                    examen = round(random.uniform(3, 9.5), 1)  # Examen sur 10
                    
                    evaluation.cc = cc
                    evaluation.examen = examen
                    
                    # Calculer la note finale pour déterminer le statut
                    note_finale = evaluation.calculer_note_finale()
                    if note_finale >= 10:
                        evaluation.statut = 'VALIDE'
                    else:
                        evaluation.statut = 'NON_VALIDE'
                    
                    evaluation.save()
                    print(f"   EC {ec.code_ec}: CC={cc}/10, Examen={examen}/10, Final={note_finale}/20 ({evaluation.statut}) [MIS À JOUR]")
                    total_evaluations += 1
            
            # Calculer et ajouter les moyennes des UE qui ont des EC
            print(f"\n   Calcul des moyennes UE:")
            for ue in ues_s1:
                ecs_de_lue = EC.objects.filter(code_ue=ue)
                if ecs_de_lue.exists():
                    # Récupérer toutes les évaluations des EC de cette UE pour cet étudiant
                    evaluations_ec = Evaluation.objects.filter(
                        matricule_etudiant=etudiant,
                        code_ec__in=ecs_de_lue
                    )
                    
                    if evaluations_ec.exists():
                        # Calculer la moyenne des notes finales des EC
                        total_notes = 0
                        count = 0
                        for eval_ec in evaluations_ec:
                            note_finale = eval_ec.calculer_note_finale()
                            if note_finale is not None:
                                total_notes += note_finale
                                count += 1
                        
                        if count > 0:
                            moyenne_ue = round(total_notes / count, 2)
                            
                            # Créer ou mettre à jour l'évaluation de l'UE avec la moyenne
                            evaluation_ue, created = Evaluation.objects.get_or_create(
                                matricule_etudiant=etudiant,
                                code_ue=ue,
                                code_ec=None,
                                defaults={
                                    'cc': None,
                                    'examen': None,
                                    'statut': 'EN_COURS'
                                }
                            )
                            
                            # Mettre les champs CC et Examen à None pour indiquer que c'est une moyenne
                            evaluation_ue.cc = None
                            evaluation_ue.examen = None
                            
                            # Déterminer le statut selon la moyenne
                            if moyenne_ue >= 10:
                                evaluation_ue.statut = 'VALIDE'
                            else:
                                evaluation_ue.statut = 'NON_VALIDE'
                            
                            evaluation_ue.save()
                            print(f"   UE {ue.code_ue}: moyenne={moyenne_ue}/20 ({evaluation_ue.statut}) [CALCULÉE]")
                            total_evaluations += 1
    
    print(f"\nGeneration terminée!")
    print(f"Statistiques:")
    print(f"   - Étudiants traités: {total_etudiants}")
    print(f"   - Cours traités: {total_cours}")
    print(f"   - Évaluations créées/mises à jour: {total_evaluations}")
    
    # Afficher quelques statistiques supplémentaires
    stats = {
        'valides': Evaluation.objects.filter(statut='VALIDE').count(),
        'non_valides': Evaluation.objects.filter(statut='NON_VALIDE').count(),
        'en_cours': Evaluation.objects.filter(statut='EN_COURS').count(),
    }
    
    print(f"\nRepartition des statuts:")
    print(f"   - Validés: {stats['valides']}")
    print(f"   - Non validés: {stats['non_valides']}")
    print(f"   - En cours: {stats['en_cours']}")

if __name__ == '__main__':
    generer_notes_l1info_s1()
