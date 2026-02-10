#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from core.models import Enseignant, Attribution
from reglage.models import TypeCharge

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("TRANSFERT DES ATTRIBUTIONS")
print("=" * 70)

cursor.execute("SELECT * FROM core_attribution")
rows = cursor.fetchall()
print(f"Nombre d'attributions dans SQLite: {len(rows)}")

count = 0
errors = []

for row in rows:
    try:
        # Récupérer l'enseignant
        enseignant = Enseignant.objects.get(matricule_en=row['matricule_en_id'])
        
        # Récupérer le type de charge
        type_charge = None
        if row['type_charge_id']:
            try:
                type_charge = TypeCharge.objects.get(code_type=row['type_charge_id'])
            except TypeCharge.DoesNotExist:
                errors.append(f"TypeCharge {row['type_charge_id']} non trouvé")
        
        # Créer l'attribution
        Attribution.objects.update_or_create(
            code_attribution=row['code_attribution'],
            defaults={
                'matricule_en': enseignant,
                'code_cours': row['code_cours'],  # CharField direct
                'annee_academique': row['annee_academique'],
                'type_charge': type_charge
            }
        )
        count += 1
        
    except Enseignant.DoesNotExist:
        errors.append(f"Enseignant {row['matricule_en_id']} non trouvé")
    except Exception as e:
        errors.append(f"Erreur {row['code_attribution']}: {str(e)[:50]}")

print(f"\n✓ {count} attributions transférées")

if errors:
    print(f"\n⚠ {len(errors)} erreurs:")
    for err in errors[:10]:
        print(f"  - {err}")

print(f"\nTotal dans MySQL: {Attribution.objects.count()}")

conn.close()
