#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from core.models import Etudiant, EC, UE, Evaluation

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("TRANSFERT DES ÉVALUATIONS")
print("=" * 70)

cursor.execute("SELECT * FROM core_evaluation")
rows = cursor.fetchall()
print(f"Nombre d'évaluations dans SQLite: {len(rows)}")

count = 0
errors = []

for row in rows:
    try:
        etudiant = Etudiant.objects.get(matricule_et=row['matricule_etudiant_id'])
        
        # Trouver l'EC ou l'UE
        ec = None
        ue = None
        
        if row['code_ec_id']:
            try:
                ec = EC.objects.get(code_ec=row['code_ec_id'])
            except EC.DoesNotExist:
                errors.append(f"EC {row['code_ec_id']} non trouvé")
                continue
        
        if row['code_ue_id']:
            try:
                ue = UE.objects.get(code_ue=row['code_ue_id'])
            except UE.DoesNotExist:
                errors.append(f"UE {row['code_ue_id']} non trouvée")
                continue
        
        # Créer l'évaluation
        Evaluation.objects.update_or_create(
            matricule_etudiant=etudiant,
            code_ue=ue,
            code_ec=ec,
            defaults={
                'cc': row['cc'],
                'examen': row['examen'],
                'rattrapage': row['rattrapage'],
                'rachat': row['rachat'],
                'statut': row['statut'] if row['statut'] else 'EN_COURS'
            }
        )
        count += 1
        
    except Exception as e:
        errors.append(f"Erreur ligne {row['id_ev']}: {str(e)[:50]}")

print(f"\n✓ {count} évaluations transférées")

if errors:
    print(f"\n⚠ {len(errors)} erreurs:")
    for err in errors[:10]:
        print(f"  - {err}")

print(f"\nTotal dans MySQL: {Evaluation.objects.count()}")

conn.close()
