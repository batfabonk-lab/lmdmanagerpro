#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from reglage.models import *
from core.models import *

print("VÉRIFICATION DES DONNÉES DANS MySQL")
print("=" * 60)

print("\n📋 TABLES DE RÉFÉRENCE (reglage)")
print(f"  Sections: {Section.objects.count()}")
print(f"  Départements: {Departement.objects.count()}")
print(f"  Mentions: {Mention.objects.count()}")
print(f"  Niveaux: {Niveau.objects.count()}")
print(f"  Semestres: {Semestre.objects.count()}")
print(f"  Classes: {Classe.objects.count()}")
print(f"  Années académiques: {AnneeAcademique.objects.count()}")
print(f"  Grades: {Grade.objects.count()}")
print(f"  Fonctions: {Fonction.objects.count()}")
print(f"  Types de charge: {TypeCharge.objects.count()}")
print(f"  Catégories: {Categorie.objects.count()}")

print("\n👥 DONNÉES PRINCIPALES (core)")
print(f"  Enseignants: {Enseignant.objects.count()}")
print(f"  Étudiants: {Etudiant.objects.count()}")
print(f"  UE: {UE.objects.count()}")
print(f"  EC: {EC.objects.count()}")
print(f"  Inscriptions: {Inscription.objects.count()}")
print(f"  Évaluations: {Evaluation.objects.count()}")
print(f"  Jury: {Jury.objects.count()}")

print("\n" + "=" * 60)

# Afficher quelques exemples
print("\nEXEMPLES DE DONNÉES:")
print("\nClasses:")
for classe in Classe.objects.all()[:5]:
    print(f"  - {classe.code_classe}: {classe.designation_classe}")

print("\nÉtudiants:")
for etudiant in Etudiant.objects.all()[:5]:
    print(f"  - {etudiant.matricule_et}: {etudiant.nom_complet}")

print("\nAnnées académiques:")
for annee in AnneeAcademique.objects.all():
    print(f"  - {annee.code_anac}: {annee.designation_anac} {'(Active)' if annee.active else ''}")
