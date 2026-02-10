#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from core.models import (User, Etudiant, Enseignant, CoursAttribution, 
                         Attribution, BulletinNotes, Deliberation, Recours)
from reglage.models import Classe, AnneeAcademique, TypeCharge

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("TRANSFERT FINAL DES DONNÉES MANQUANTES")
print("=" * 70)

# 1. ATTRIBUTIONS (core_attribution)
print("\n📝 Transfert des Attributions...")
cursor.execute("SELECT * FROM core_attribution")
count = 0
errors = []
for row in cursor.fetchall():
    try:
        enseignant = Enseignant.objects.get(matricule_en=row['matricule_en_id'])
        # code_cours est directement le code, pas une FK
        type_charge = TypeCharge.objects.get(code_type=row['type_charge_id'])
        
        Attribution.objects.update_or_create(
            code_attribution=row['code_attribution'],
            defaults={
                'matricule_en': enseignant,
                'code_cours_id': row['code_cours'],  # Référence au CoursAttribution
                'annee_academique': row['annee_academique'],
                'type_charge': type_charge,
                'volume_horaire': 0,  # Pas dans SQLite
                'date_attribution': row['date_attribution']
            }
        )
        count += 1
    except Exception as e:
        errors.append(str(e)[:50])
        
print(f"  ✓ {count} attributions transférées")
if errors and len(errors) <= 3:
    for err in errors[:3]:
        print(f"    ⚠ {err}")

# 2. BULLETINS DE NOTES
print("\n📄 Transfert des Bulletins de Notes...")
cursor.execute("SELECT * FROM core_bulletinnotes")
count = 0
for row in cursor.fetchall():
    try:
        etudiant = Etudiant.objects.get(matricule_et=row['etudiant_id'])
        classe = Classe.objects.get(code_classe=row['code_classe_id'])
        genere_par = User.objects.get(id=row['genere_par_id']) if row['genere_par_id'] else None
        
        BulletinNotes.objects.update_or_create(
            etudiant=etudiant,
            annee_academique=row['annee_academique'],
            code_classe=classe,
            defaults={
                'fichier_pdf': row['fichier_pdf'] or '',
                'date_generation': row['date_generation'],
                'disponible': bool(row['disponible']),
                'genere_par': genere_par
            }
        )
        count += 1
    except Exception as e:
        pass
        
print(f"  ✓ {count} bulletins transférés")

# 3. DÉLIBÉRATIONS
print("\n⚖️ Transfert des Délibérations...")
cursor.execute("SELECT * FROM core_deliberation")
count = 0
for row in cursor.fetchall():
    try:
        classe = Classe.objects.get(code_classe=row['code_classe_id'])
        cree_par = User.objects.get(id=row['cree_par_id']) if row['cree_par_id'] else None
        
        Deliberation.objects.update_or_create(
            code_classe=classe,
            annee_academique=row['annee_academique'],
            type_deliberation=row['type_deliberation'],
            defaults={
                'semestre': row['semestre'],
                'payload': row['payload'] or '',
                'date_creation': row['date_creation'],
                'date_mise_a_jour': row['date_mise_a_jour'],
                'cree_par': cree_par
            }
        )
        count += 1
    except Exception as e:
        pass
        
print(f"  ✓ {count} délibérations transférées")

# 4. RECOURS
print("\n📮 Transfert des Recours...")
cursor.execute("SELECT * FROM core_recours")
count = 0
for row in cursor.fetchall():
    try:
        etudiant = Etudiant.objects.get(matricule_et=row['etudiant_id'])
        traite_par = User.objects.get(id=row['traite_par_id']) if row['traite_par_id'] else None
        
        Recours.objects.update_or_create(
            code_recours=row['code_recours'],
            defaults={
                'etudiant': etudiant,
                'objet': row['objet'] or 'autre',
                'ue_ec_concerne': row['ue_ec_concerne'] or '',
                'description': row['description'] or '',
                'date_envoi': row['date_envoi'],
                'statut': row['statut'] or 'EN_ATTENTE',
                'date_traitement': row['date_traitement'],
                'commentaire_traitement': row['commentaire_traitement'] or '',
                'traite_par': traite_par
            }
        )
        count += 1
    except Exception as e:
        pass
        
print(f"  ✓ {count} recours transférés")

conn.close()

print("\n" + "=" * 70)
print("✅ TRANSFERT FINAL TERMINÉ!")

print("\n📊 RÉSUMÉ:")
print(f"  • Attributions: {Attribution.objects.count()}")
print(f"  • Bulletins: {BulletinNotes.objects.count()}")
print(f"  • Délibérations: {Deliberation.objects.count()}")
print(f"  • Recours: {Recours.objects.count()}")
