#!/usr/bin/env python
import os
import django
import sqlite3
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from core.models import (User, Etudiant, Enseignant, Jury as JuryModel, 
                         CoursAttribution, BulletinNotes, Deliberation, 
                         PresenceDeliberation, Recours)
from reglage.models import Classe, AnneeAcademique

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("TRANSFERT DES TABLES MANQUANTES")
print("=" * 70)

# 1. USERS (core_user)
print("\n👤 Transfert des Utilisateurs (core_user)...")
cursor.execute("SELECT * FROM core_user")
count = 0
for row in cursor.fetchall():
    try:
        user, created = User.objects.update_or_create(
            id=row['id'],
            defaults={
                'username': row['username'],
                'first_name': row['first_name'] or '',
                'last_name': row['last_name'] or '',
                'email': row['email'] or '',
                'password': row['password'],
                'is_staff': bool(row['is_staff']),
                'is_active': bool(row['is_active']),
                'is_superuser': bool(row['is_superuser']),
                'date_joined': row['date_joined'],
                'last_login': row['last_login'],
                'role': row['role'] if row['role'] else 'ETUDIANT'
            }
        )
        count += 1
    except Exception as e:
        print(f"  ✗ Erreur user {row['username']}: {str(e)[:50]}")
print(f"  ✓ {count} utilisateurs transférés")

# 2. CONTENT TYPES (django_content_type)
print("\n📦 Transfert des Content Types...")
cursor.execute("SELECT * FROM django_content_type")
count = 0
for row in cursor.fetchall():
    try:
        ContentType.objects.update_or_create(
            id=row['id'],
            defaults={
                'app_label': row['app_label'],
                'model': row['model']
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} content types transférés")

# 3. PERMISSIONS (auth_permission)
print("\n🔐 Transfert des Permissions...")
cursor.execute("SELECT * FROM auth_permission")
count = 0
for row in cursor.fetchall():
    try:
        content_type = ContentType.objects.get(id=row['content_type_id'])
        Permission.objects.update_or_create(
            id=row['id'],
            defaults={
                'name': row['name'],
                'content_type': content_type,
                'codename': row['codename']
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} permissions transférées")

# 4. COURS ATTRIBUTION (cours_attribution)
print("\n📚 Transfert des Attributions de Cours (cours_attribution)...")
cursor.execute("SELECT * FROM cours_attribution")
count = 0
for row in cursor.fetchall():
    try:
        CoursAttribution.objects.update_or_create(
            code_cours=row['code_cours'],
            defaults={
                'intitule': row['intitule'],
                'type_cours': row['type_cours'],
                'code_ue_parent': row['code_ue_parent'],
                'credit': row['credit'],
                'semestre': row['semestre'],
                'classe_id': row['classe_id']
            }
        )
        count += 1
    except Exception as e:
        pass
print(f"  ✓ {count} cours attributions transférés")

# 5. CORE ATTRIBUTION (core_attribution)
print("\n📝 Transfert des Attributions (core_attribution)...")
cursor.execute("SELECT * FROM core_attribution")
count = 0
for row in cursor.fetchall():
    try:
        # Cette table semble être une relation many-to-many
        # On va essayer de la créer si le modèle existe
        pass  # À adapter selon la structure exacte du modèle
    except:
        pass
print(f"  ⚠ core_attribution nécessite une analyse plus approfondie")

# 6. BULLETINS DE NOTES
print("\n📄 Transfert des Bulletins de Notes...")
cursor.execute("SELECT * FROM core_bulletinnotes")
count = 0
for row in cursor.fetchall():
    try:
        from core.models import Inscription
        inscription = Inscription.objects.get(code_inscription=row['matricule_id'])
        BulletinNotes.objects.update_or_create(
            matricule=inscription,
            defaults={
                'moyenne_generale': row['moyenne_generale'],
                'credits_capitalises': row['credits_capitalises'],
                'credits_non_capitalises': row['credits_non_capitalises'],
                'decision': row['decision'] or '',
                'date_generation': row['date_generation']
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} bulletins transférés")

# 7. DÉLIBÉRATIONS
print("\n⚖️ Transfert des Délibérations...")
cursor.execute("SELECT * FROM core_deliberation")
count = 0
for row in cursor.fetchall():
    try:
        classe = Classe.objects.get(code_classe=row['code_classe_id'])
        annee = AnneeAcademique.objects.get(code_anac=row['annee_academique'])
        Deliberation.objects.update_or_create(
            code_deliberation=row['code_deliberation'],
            defaults={
                'code_classe': classe,
                'annee_academique': annee,
                'date_deliberation': row['date_deliberation'],
                'statut': row['statut'] or 'EN_ATTENTE'
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} délibérations transférées")

# 8. PRÉSENCES DÉLIBÉRATION
print("\n✅ Transfert des Présences Délibération...")
cursor.execute("SELECT * FROM core_presencedeliberation")
count = 0
for row in cursor.fetchall():
    try:
        deliberation = Deliberation.objects.get(code_deliberation=row['deliberation_id'])
        enseignant = Enseignant.objects.get(matricule_en=row['enseignant_id'])
        PresenceDeliberation.objects.update_or_create(
            deliberation=deliberation,
            enseignant=enseignant,
            defaults={
                'present': bool(row['present']),
                'role': row['role'] or ''
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} présences transférées")

# 9. RECOURS
print("\n📮 Transfert des Recours...")
cursor.execute("SELECT * FROM core_recours")
count = 0
for row in cursor.fetchall():
    try:
        from core.models import Inscription
        inscription = Inscription.objects.get(code_inscription=row['matricule_id'])
        Recours.objects.update_or_create(
            code_recours=row['code_recours'],
            defaults={
                'matricule': inscription,
                'motif': row['motif'] or '',
                'statut': row['statut'] or 'EN_ATTENTE',
                'date_soumission': row['date_soumission'],
                'date_traitement': row['date_traitement']
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} recours transférés")

conn.close()

print("\n" + "=" * 70)
print("✅ TRANSFERT DES TABLES MANQUANTES TERMINÉ!")

# Résumé
print("\n📊 RÉSUMÉ:")
print(f"  • Utilisateurs: {User.objects.count()}")
print(f"  • Content Types: {ContentType.objects.count()}")
print(f"  • Permissions: {Permission.objects.count()}")
print(f"  • Cours Attributions: {CoursAttribution.objects.count()}")
print(f"  • Bulletins: {BulletinNotes.objects.count()}")
print(f"  • Délibérations: {Deliberation.objects.count()}")
print(f"  • Présences Délibération: {PresenceDeliberation.objects.count()}")
print(f"  • Recours: {Recours.objects.count()}")
