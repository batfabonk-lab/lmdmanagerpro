#!/usr/bin/env python
import os
import sys
import django

# Configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from django.db import connections
from core.models import *
from reglage.models import *

def check_data():
    """Vérifier les données dans MySQL"""
    print("Vérification des données dans MySQL:")
    
    models_to_check = [
        ('AnneeAcademique', AnneeAcademique),
        ('Departement', Departement),
        ('Enseignant', Enseignant),
        ('Etudiant', Etudiant),
        ('UE', UE),
        ('EC', EC),
        ('Inscription', Inscription),
        ('Evaluation', Evaluation),
        ('Jury', Jury),
        ('BulletinNotes', BulletinNotes),
    ]
    
    for name, model in models_to_check:
        try:
            count = model.objects.count()
            print(f"  {name}: {count} enregistrements")
        except Exception as e:
            print(f"  Erreur avec {name}: {e}")

def create_sample_data():
    """Créer des données de test si nécessaire"""
    print("Création de données de test...")
    
    try:
        # Année académique
        annee, created = AnneeAcademique.objects.get_or_create(
            code="2024-2025",
            defaults={
                'debut': '2024-10-01',
                'fin': '2025-07-31',
                'active': True
            }
        )
        print(f"  Année académique: {'créée' if created else 'existante'}")
        
        # Département
        dept, created = Departement.objects.get_or_create(
            code="INFO",
            defaults={'nom': 'Informatique'}
        )
        print(f"  Département: {'créé' if created else 'existant'}")
        
        # Mention
        mention, created = Mention.objects.get_or_create(
            code="LINFO",
            defaults={'nom': 'Licence Informatique'}
        )
        print(f"  Mention: {'créée' if created else 'existante'}")
        
        # Niveau
        niveau, created = Niveau.objects.get_or_create(
            code="L1",
            defaults={'nom': 'Licence 1'}
        )
        print(f"  Niveau: {'créé' if created else 'existant'}")
        
        # Classe
        classe, created = Classe.objects.get_or_create(
            code="L1INFO",
            defaults={
                'nom': 'Licence 1 Informatique',
                'departement': dept,
                'mention': mention,
                'niveau': niveau
            }
        )
        print(f"  Classe: {'créée' if created else 'existante'}")
        
        # Enseignant
        enseignant, created = Enseignant.objects.get_or_create(
            id_lgn="ENS001",
            defaults={
                'nom': 'Dupont',
                'postnom': 'Jean',
                'prenom': 'Pierre',
                'grade': Grade.objects.first(),
                'fonction': Fonction.objects.first(),
                'departement': dept,
                'telephone': '0123456789',
                'email': 'jean.dupont@example.com'
            }
        )
        print(f"  Enseignant: {'créé' if created else 'existant'}")
        
        # Étudiant
        etudiant, created = Etudiant.objects.get_or_create(
            id_lgn="ETU001",
            defaults={
                'nom': 'Martin',
                'postnom': 'Sophie',
                'prenom': 'Marie',
                'sexe': 'F',
                'lieu_naissance': 'Kinshasa',
                'date_naissance': '2000-01-01',
                'nationalite': 'Congolaise',
                'telephone': '0987654321',
                'email': 'sophie.martin@example.com'
            }
        )
        print(f"  Étudiant: {'créé' if created else 'existant'}")
        
        # UE
        ue, created = UE.objects.get_or_create(
            code="INFO101",
            defaults={
                'nom': 'Algorithmique',
                'credits': 6,
                'seuil': 10,
                'categorie': Categorie.objects.first(),
                'classe': classe
            }
        )
        print(f"  UE: {'créée' if created else 'existante'}")
        
        # EC
        ec, created = EC.objects.get_or_create(
            code="INFO101A",
            defaults={
                'nom': 'Algorithmique Théorique',
                'credits': 3,
                'seuil': 10,
                'categorie': Categorie.objects.first(),
                'ue': ue,
                'classe': classe
            }
        )
        print(f"  EC: {'créé' if created else 'existant'}")
        
        # Inscription
        inscription, created = Inscription.objects.get_or_create(
            matricule="MAT2024001",
            defaults={
                'etudiant': etudiant,
                'classe': classe,
                'annee_academique': annee,
                'cohorte': '2024'
            }
        )
        print(f"  Inscription: {'créée' if created else 'existante'}")
        
        print("Données de test créées avec succès!")
        
    except Exception as e:
        print(f"Erreur lors de la création des données: {e}")

def main():
    """Fonction principale"""
    print("Transfert et vérification des données")
    print("=" * 40)
    
    # Vérifier les données actuelles
    check_data()
    
    print("\n" + "=" * 40)
    
    # Créer des données de test si nécessaire
    create_sample_data()
    
    print("\n" + "=" * 40)
    
    # Vérifier à nouveau
    check_data()

if __name__ == '__main__':
    main()
