#!/usr/bin/env python
import os
import sys
import django

# Configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from reglage.models import *
from core.models import *

def create_basic_data():
    """Créer les données de base pour le système"""
    print("Création des données de base pour MySQL...")
    
    try:
        # Section
        section, created = Section.objects.get_or_create(
            code_section="SCI",
            defaults={'designation_section': 'Sciences'}
        )
        print(f"  Section: {'créée' if created else 'existante'}")
        
        # Département
        dept, created = Departement.objects.get_or_create(
            code_departement="INFO",
            defaults={
                'designation_departement': 'Informatique',
                'code_section': section
            }
        )
        print(f"  Département: {'créé' if created else 'existant'}")
        
        # Mention
        mention, created = Mention.objects.get_or_create(
            code_mention="LINFO",
            defaults={'designation_mention': 'Licence Informatique'}
        )
        print(f"  Mention: {'créée' if created else 'existante'}")
        
        # Niveau
        niveau, created = Niveau.objects.get_or_create(
            code_niveau="L1",
            defaults={'designation_niveau': 'Licence 1'}
        )
        print(f"  Niveau: {'créé' if created else 'existant'}")
        
        # Semestre
        semestre1, created = Semestre.objects.get_or_create(
            code_semestre="S1",
            defaults={'designation_semestre': 'Semestre 1'}
        )
        print(f"  Semestre 1: {'créé' if created else 'existant'}")
        
        semestre2, created = Semestre.objects.get_or_create(
            code_semestre="S2",
            defaults={'designation_semestre': 'Semestre 2'}
        )
        print(f"  Semestre 2: {'créé' if created else 'existant'}")
        
        # Classe
        classe, created = Classe.objects.get_or_create(
            code_classe="L1INFO",
            defaults={
                'designation_classe': 'Licence 1 Informatique',
                'code_niveau': niveau,
                'code_mention': mention
            }
        )
        print(f"  Classe: {'créée' if created else 'existante'}")
        
        # Année académique
        annee, created = AnneeAcademique.objects.get_or_create(
            code_anac="2024-2025",
            defaults={
                'designation_anac': 'Année Académique 2024-2025',
                'date_debut': '2024-10-01',
                'date_fin': '2025-07-31',
                'active': True
            }
        )
        print(f"  Année académique: {'créée' if created else 'existante'}")
        
        # Catégories
        cat_a, created = Categorie.objects.get_or_create(
            code_categorie="A",
            defaults={'designation_categorie': 'Catégorie A'}
        )
        print(f"  Catégorie A: {'créée' if created else 'existante'}")
        
        cat_b, created = Categorie.objects.get_or_create(
            code_categorie="B",
            defaults={'designation_categorie': 'Catégorie B'}
        )
        print(f"  Catégorie B: {'créée' if created else 'existante'}")
        
        # Grades
        grade1, created = Grade.objects.get_or_create(
            code_grade="ASS",
            defaults={'designation_grade': 'Assistant'}
        )
        print(f"  Grade Assistant: {'créé' if created else 'existant'}")
        
        grade2, created = Grade.objects.get_or_create(
            code_grade="PROF",
            defaults={'designation_grade': 'Professeur'}
        )
        print(f"  Grade Professeur: {'créé' if created else 'existant'}")
        
        # Fonctions
        fonction1, created = Fonction.objects.get_or_create(
            code_fonction="ENS",
            defaults={'designation_fonction': 'Enseignant'}
        )
        print(f"  Fonction Enseignant: {'créée' if created else 'existante'}")
        
        fonction2, created = Fonction.objects.get_or_create(
            code_fonction="CHEF",
            defaults={'designation_fonction': 'Chef de Département'}
        )
        print(f"  Fonction Chef: {'créée' if created else 'existante'}")
        
        # Type de charge
        type_charge, created = TypeCharge.objects.get_or_create(
            code_typecharge="TD",
            defaults={'designation_typecharge': 'Travaux Dirigés'}
        )
        print(f"  Type charge TD: {'créé' if created else 'existant'}")
        
        # Enseignant
        enseignant, created = Enseignant.objects.get_or_create(
            id_lgn="ENS001",
            defaults={
                'nom': 'Dupont',
                'postnom': 'Jean',
                'prenom': 'Pierre',
                'sexe': 'M',
                'grade': grade1,
                'fonction': fonction1,
                'code_departement': dept,
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
        ue1, created = UE.objects.get_or_create(
            code="INFO101",
            defaults={
                'nom': 'Algorithmique',
                'credits': 6,
                'seuil': 10,
                'code_categorie': cat_a,
                'code_classe': classe
            }
        )
        print(f"  UE Algorithmique: {'créée' if created else 'existante'}")
        
        ue2, created = UE.objects.get_or_create(
            code="INFO102",
            defaults={
                'nom': 'Programmation',
                'credits': 6,
                'seuil': 10,
                'code_categorie': cat_a,
                'code_classe': classe
            }
        )
        print(f"  UE Programmation: {'créée' if created else 'existante'}")
        
        # EC
        ec1, created = EC.objects.get_or_create(
            code="INFO101A",
            defaults={
                'nom': 'Algorithmique Théorique',
                'credits': 3,
                'seuil': 10,
                'code_categorie': cat_a,
                'code_ue': ue1,
                'code_classe': classe
            }
        )
        print(f"  EC Algorithmique Théorique: {'créé' if created else 'existant'}")
        
        ec2, created = EC.objects.get_or_create(
            code="INFO101B",
            defaults={
                'nom': 'Algorithmique Pratique',
                'credits': 3,
                'seuil': 10,
                'code_categorie': cat_a,
                'code_ue': ue1,
                'code_classe': classe
            }
        )
        print(f"  EC Algorithmique Pratique: {'créé' if created else 'existant'}")
        
        # Inscription
        inscription, created = Inscription.objects.get_or_create(
            matricule="MAT2024001",
            defaults={
                'id_lgn': etudiant,
                'code_classe': classe,
                'code_anac': annee,
                'cohorte': '2024'
            }
        )
        print(f"  Inscription: {'créée' if created else 'existante'}")
        
        print("\nDonnées de base créées avec succès!")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la création des données: {e}")
        return False

def check_data():
    """Vérifier les données créées"""
    print("\nVérification des données dans MySQL:")
    
    models_to_check = [
        ('Section', Section),
        ('Departement', Departement),
        ('Mention', Mention),
        ('Niveau', Niveau),
        ('Classe', Classe),
        ('AnneeAcademique', AnneeAcademique),
        ('Categorie', Categorie),
        ('Grade', Grade),
        ('Fonction', Fonction),
        ('TypeCharge', TypeCharge),
        ('Enseignant', Enseignant),
        ('Etudiant', Etudiant),
        ('UE', UE),
        ('EC', EC),
        ('Inscription', Inscription),
    ]
    
    for name, model in models_to_check:
        try:
            count = model.objects.count()
            print(f"  {name}: {count} enregistrements")
        except Exception as e:
            print(f"  Erreur avec {name}: {e}")

def main():
    """Fonction principale"""
    print("Configuration des données MySQL pour LMD Manager")
    print("=" * 50)
    
    # Créer les données de base
    if create_basic_data():
        # Vérifier les données
        check_data()
        print("\nConfiguration terminée avec succès!")
    else:
        print("\nErreur lors de la configuration!")

if __name__ == '__main__':
    main()
