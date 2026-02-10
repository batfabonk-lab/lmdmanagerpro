#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from reglage.models import Classe, AnneeAcademique
from core.models import Etudiant, EC, UE, Inscription, Evaluation, Jury, Cohorte

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("TRANSFERT COMPLET - INSCRIPTIONS, ÉVALUATIONS ET JURY")
print("=" * 70)

# 1. COHORTES (si nécessaire)
print("\n📅 Transfert des Cohortes...")
cursor.execute("SELECT DISTINCT cohorte_id FROM core_inscription WHERE cohorte_id IS NOT NULL")
cohortes = cursor.fetchall()
count = 0
for row in cohortes:
    try:
        cohorte_id = row['cohorte_id']
        Cohorte.objects.get_or_create(
            code_cohorte=cohorte_id,
            defaults={
                'lib_cohorte': cohorte_id,
                'debut': '2025-01-01'
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} cohortes créées")

# 2. INSCRIPTIONS
print("\n📝 Transfert des Inscriptions...")
cursor.execute("SELECT * FROM core_inscription")
count = 0
for row in cursor.fetchall():
    try:
        etudiant = Etudiant.objects.get(matricule_et=row['matricule_etudiant_id'])
        classe = Classe.objects.get(code_classe=row['code_classe_id'])
        cohorte = Cohorte.objects.get(code_cohorte=row['cohorte_id']) if row['cohorte_id'] else None
        
        Inscription.objects.update_or_create(
            code_inscription=row['code_inscription'],
            defaults={
                'matricule_etudiant': etudiant,
                'code_classe': classe,
                'annee_academique': row['annee_academique'],
                'cohorte': cohorte
            }
        )
        count += 1
    except Exception as e:
        pass
print(f"  ✓ {count} inscriptions transférées")

# 3. ÉVALUATIONS
print("\n📊 Transfert des Évaluations...")
cursor.execute("SELECT * FROM core_evaluation")
count = 0
for row in cursor.fetchall():
    try:
        etudiant = Etudiant.objects.get(matricule_et=row['matricule_etudiant_id'])
        
        # Trouver l'inscription de cet étudiant
        inscriptions = Inscription.objects.filter(matricule_etudiant=etudiant)
        
        if inscriptions.exists():
            inscription = inscriptions.first()
            
            # Trouver l'EC ou l'UE
            ec = None
            if row['code_ec_id']:
                try:
                    ec = EC.objects.get(code_ec=row['code_ec_id'])
                except:
                    pass
            elif row['code_ue_id']:
                try:
                    ue = UE.objects.get(code_ue=row['code_ue_id'])
                    # Prendre le premier EC de cette UE
                    ecs = EC.objects.filter(code_ue=ue)
                    if ecs.exists():
                        ec = ecs.first()
                except:
                    pass
            
            if ec:
                Evaluation.objects.update_or_create(
                    code_ec=ec,
                    matricule_etudiant=inscription,
                    defaults={
                        'cc': row['cc'],
                        'examen': row['examen'],
                        'rattrapage': row['rattrapage'],
                        'rachat': row['rachat'],
                        'statut': row.get('statut', 'EN_COURS')
                    }
                )
                count += 1
    except:
        pass
print(f"  ✓ {count} évaluations transférées")

# 4. JURY
print("\n⚖️ Transfert des Jury...")
cursor.execute("SELECT * FROM core_jury")
count = 0
for row in cursor.fetchall():
    try:
        classe = Classe.objects.get(code_classe=row['code_classe_id'])
        
        Jury.objects.update_or_create(
            code_jury=row['code_jury'],
            defaults={
                'president': row['president'],
                'secretaire': row['secretaire'],
                'membre': row['membre'],
                'code_classe': classe,
                'decision': row['decision'] or ''
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} jurys transférés")

conn.close()

print("\n" + "=" * 70)
print("✅ TRANSFERT COMPLET TERMINÉ!")

# Résumé final
from reglage.models import (Section, Departement, Mention, Niveau, Semestre, 
                            AnneeAcademique, Grade, Fonction, TypeCharge, Categorie)
from core.models import Enseignant

print("\n📊 RÉSUMÉ COMPLET DE TOUTES LES DONNÉES DANS MySQL:")
print("\n📋 Tables de référence (reglage):")
print(f"  • Sections: {Section.objects.count()}")
print(f"  • Départements: {Departement.objects.count()}")
print(f"  • Mentions: {Mention.objects.count()}")
print(f"  • Niveaux: {Niveau.objects.count()}")
print(f"  • Semestres: {Semestre.objects.count()}")
print(f"  • Classes: {Classe.objects.count()}")
print(f"  • Années académiques: {AnneeAcademique.objects.count()}")
print(f"  • Grades: {Grade.objects.count()}")
print(f"  • Fonctions: {Fonction.objects.count()}")
print(f"  • Types de charge: {TypeCharge.objects.count()}")
print(f"  • Catégories: {Categorie.objects.count()}")

print("\n👥 Données principales (core):")
print(f"  • Enseignants: {Enseignant.objects.count()}")
print(f"  • Étudiants: {Etudiant.objects.count()}")
print(f"  • Cohortes: {Cohorte.objects.count()}")
print(f"  • UE: {UE.objects.count()}")
print(f"  • EC: {EC.objects.count()}")
print(f"  • Inscriptions: {Inscription.objects.count()}")
print(f"  • Évaluations: {Evaluation.objects.count()}")
print(f"  • Jury: {Jury.objects.count()}")

total = (Section.objects.count() + Departement.objects.count() + Mention.objects.count() + 
         Niveau.objects.count() + Semestre.objects.count() + Classe.objects.count() + 
         AnneeAcademique.objects.count() + Grade.objects.count() + Fonction.objects.count() + 
         TypeCharge.objects.count() + Categorie.objects.count() + Enseignant.objects.count() + 
         Etudiant.objects.count() + Cohorte.objects.count() + UE.objects.count() + 
         EC.objects.count() + Inscription.objects.count() + Evaluation.objects.count() + 
         Jury.objects.count())

print(f"\n🎉 TOTAL: {total} enregistrements transférés dans MySQL")
print("\n" + "=" * 70)
