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

print("TRANSFERT UE ET EC")
print("=" * 60)

# UE
print("\n📚 Transfert des UE...")
cursor.execute("SELECT * FROM core_ue")
count = 0
errors = 0
for row in cursor.fetchall():
    try:
        classe = Classe.objects.get(code_classe=row['classe_id']) if row['classe_id'] else None
        UE.objects.update_or_create(
            code_ue=row['code_ue'],
            defaults={
                'intitule_ue': row['intitule_ue'],
                'credit': row['credit'],
                'semestre': row['semestre'] or 1,
                'seuil': row['seuil'] or 50,
                'categorie': row['categorie'] or 'A',
                'classe': classe
            }
        )
        count += 1
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(f"  ✗ Erreur UE {row['code_ue']}: {e}")
print(f"  ✓ {count} UE transférées ({errors} erreurs)")

# EC
print("\n📖 Transfert des EC...")
cursor.execute("SELECT * FROM core_ec")
count = 0
errors = 0
for row in cursor.fetchall():
    try:
        ue = UE.objects.get(code_ue=row['code_ue_id']) if row['code_ue_id'] else None
        classe = Classe.objects.get(code_classe=row['code_classe_id']) if row['code_classe_id'] else None
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
            print(f"  ✗ Erreur EC {row['code_ec']}: {e}")
print(f"  ✓ {count} EC transférés ({errors} erreurs)")

conn.close()

print("\n" + "=" * 60)
print("✅ TRANSFERT TERMINÉ!")
print(f"\nRésumé:")
print(f"  UE dans MySQL: {UE.objects.count()}")
print(f"  EC dans MySQL: {EC.objects.count()}")
