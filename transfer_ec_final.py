#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from reglage.models import Classe
from core.models import UE, EC

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("TRANSFERT DES EC")
print("=" * 60)

cursor.execute("SELECT * FROM core_ec")
count = 0
errors = 0
for row in cursor.fetchall():
    try:
        ue = UE.objects.get(code_ue=row['code_ue_id']) if row['code_ue_id'] else None
        classe = Classe.objects.get(code_classe=row['classe_id']) if row['classe_id'] else None
        EC.objects.update_or_create(
            code_ec=row['code_ec'],
            defaults={
                'intitule_ue': row['intitule_ue'],
                'credit': row['credit'],
                'seuil': row['seuil'] or 8,
                'categorie': row['categorie'] or '',
                'code_ue': ue,
                'classe': classe
            }
        )
        count += 1
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(f"  ✗ {row['code_ec']}: {e}")

conn.close()

print(f"\n✓ {count} EC transférés ({errors} erreurs)")
print(f"\nTotal EC dans MySQL: {EC.objects.count()}")
