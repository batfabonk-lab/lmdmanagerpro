#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from reglage.models import Classe, AnneeAcademique
from core.models import Etudiant, Inscription

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("TRANSFERT DES INSCRIPTIONS AVEC DEBUG")
print("=" * 60)

cursor.execute("SELECT * FROM core_inscription")
rows = cursor.fetchall()
print(f"\nNombre d'inscriptions dans SQLite: {len(rows)}")

count = 0
for row in rows:
    try:
        print(f"\nTraitement de {row['code_inscription']}...")
        
        etudiant = Etudiant.objects.get(matricule_et=row['matricule_etudiant_id'])
        print(f"  ✓ Étudiant: {etudiant.nom_complet}")
        
        classe = Classe.objects.get(code_classe=row['code_classe_id'])
        print(f"  ✓ Classe: {classe.designation_classe}")
        
        annee = AnneeAcademique.objects.get(code_anac=row['annee_academique'])
        print(f"  ✓ Année: {annee.designation_anac}")
        
        inscription, created = Inscription.objects.update_or_create(
            matricule=row['code_inscription'],
            defaults={
                'matricule_et': etudiant,
                'code_classe': classe,
                'code_anac': annee,
                'cohorte': row['cohorte_id'] or ''
            }
        )
        print(f"  ✓ Inscription {'créée' if created else 'mise à jour'}")
        count += 1
        
    except Exception as e:
        print(f"  ✗ ERREUR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

conn.close()

print("\n" + "=" * 60)
print(f"✅ {count} inscriptions transférées")
print(f"Total dans MySQL: {Inscription.objects.count()}")
