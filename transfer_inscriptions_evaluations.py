#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from reglage.models import Classe, AnneeAcademique
from core.models import UE, EC, Etudiant, Inscription, Evaluation, Jury

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("TRANSFERT INSCRIPTIONS, ÉVALUATIONS ET JURY")
print("=" * 60)

# Vérifier la structure de core_inscription
print("\nStructure de core_inscription:")
cursor.execute("PRAGMA table_info(core_inscription)")
cols = [col[1] for col in cursor.fetchall()]
print(f"  Colonnes: {', '.join(cols)}")

# Inscriptions
print("\n📝 Transfert des Inscriptions...")
cursor.execute("SELECT * FROM core_inscription")
count = 0
errors = 0
for row in cursor.fetchall():
    try:
        # Trouver l'étudiant par matricule_et
        etudiant = Etudiant.objects.get(matricule_et=row['matricule_et_id'])
        classe = Classe.objects.get(code_classe=row['code_classe_id'])
        annee = AnneeAcademique.objects.get(code_anac=row['code_anac_id'])
        
        Inscription.objects.update_or_create(
            matricule=row['matricule'],
            defaults={
                'matricule_et': etudiant,
                'code_classe': classe,
                'code_anac': annee,
                'cohorte': row['cohorte'] or ''
            }
        )
        count += 1
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(f"  ✗ Erreur: {e}")
print(f"  ✓ {count} inscriptions transférées ({errors} erreurs)")

# Évaluations
print("\n📊 Transfert des Évaluations...")
cursor.execute("SELECT * FROM core_evaluation")
count = 0
errors = 0
for row in cursor.fetchall():
    try:
        ec = EC.objects.get(code_ec=row['code_ec_id'])
        inscription = Inscription.objects.get(matricule=row['matricule_id'])
        
        Evaluation.objects.update_or_create(
            code_ec=ec,
            matricule=inscription,
            defaults={
                'cc': row['cc'],
                'examen': row['examen'],
                'rattrapage': row['rattrapage'],
                'rachat': row['rachat'],
                'enseignement': row['enseignement']
            }
        )
        count += 1
    except Exception as e:
        errors += 1
print(f"  ✓ {count} évaluations transférées ({errors} erreurs)")

# Jury
print("\n⚖️ Transfert des Jury...")
cursor.execute("SELECT * FROM core_jury")
count = 0
errors = 0
for row in cursor.fetchall():
    try:
        inscription = Inscription.objects.get(matricule=row['matricule_id'])
        
        Jury.objects.update_or_create(
            matricule_et=inscription,
            defaults={'decision': row['decision'] or ''}
        )
        count += 1
    except Exception as e:
        errors += 1
print(f"  ✓ {count} jurys transférés ({errors} erreurs)")

conn.close()

print("\n" + "=" * 60)
print("✅ TRANSFERT TERMINÉ!")

print("\n📊 RÉSUMÉ FINAL:")
print(f"  Étudiants: {Etudiant.objects.count()}")
print(f"  Classes: {Classe.objects.count()}")
print(f"  UE: {UE.objects.count()}")
print(f"  EC: {EC.objects.count()}")
print(f"  Inscriptions: {Inscription.objects.count()}")
print(f"  Évaluations: {Evaluation.objects.count()}")
print(f"  Jury: {Jury.objects.count()}")
