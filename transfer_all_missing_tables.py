#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from core.models import (User, Etudiant, Enseignant, CoursAttribution, 
                         Attribution, BulletinNotes, Deliberation, 
                         Recours, FichierRecours, Notification,
                         CommentaireCours, EvaluationEnseignement,
                         CommuniqueDeliberation, ParametreEvaluation)
from reglage.models import Classe, AnneeAcademique

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("TRANSFERT DE TOUTES LES TABLES MANQUANTES")
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
        pass
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
print("\n📚 Transfert des Cours Attributions...")
cursor.execute("SELECT * FROM cours_attribution")
count = 0
for row in cursor.fetchall():
    try:
        CoursAttribution.objects.update_or_create(
            code_cours=row['code_cours'],
            defaults={
                'intitule': row['intitule'],
                'type_cours': row['type_cours'],
                'code_ue_parent': row['code_ue_parent'] or '',
                'credit': row['credit'],
                'semestre': row['semestre'],
                'classe_id': row['classe_id']
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} cours attributions transférés")

# 5. CORE ATTRIBUTION (core_attribution)
print("\n📝 Transfert des Attributions...")
cursor.execute("SELECT * FROM core_attribution")
count = 0
for row in cursor.fetchall():
    try:
        enseignant = Enseignant.objects.get(matricule_en=row['matricule_en_id'])
        cours = CoursAttribution.objects.get(code_cours=row['code_cours_id'])
        annee = AnneeAcademique.objects.get(code_anac=row['annee_academique'])
        
        Attribution.objects.update_or_create(
            code_attribution=row['code_attribution'],
            defaults={
                'matricule_en': enseignant,
                'code_cours': cours,
                'annee_academique': annee,
                'type_charge_id': row['type_charge_id'],
                'volume_horaire': row['volume_horaire'] or 0
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} attributions transférées")

# 6. BULLETINS DE NOTES
print("\n📄 Transfert des Bulletins de Notes...")
cursor.execute("SELECT * FROM core_bulletinnotes")
count = 0
for row in cursor.fetchall():
    try:
        etudiant = Etudiant.objects.get(matricule_et=row['etudiant_id'])
        classe = Classe.objects.get(code_classe=row['code_classe_id'])
        
        BulletinNotes.objects.update_or_create(
            etudiant=etudiant,
            annee_academique=row['annee_academique'],
            code_classe=classe,
            defaults={
                'moyenne_generale': row['moyenne_generale'],
                'credits_capitalises': row['credits_capitalises'],
                'credits_non_capitalises': row['credits_non_capitalises'],
                'decision': row['decision'] or ''
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
        
        Deliberation.objects.update_or_create(
            code_classe=classe,
            annee_academique=row['annee_academique'],
            type_deliberation=row['type_deliberation'],
            defaults={
                'date_deliberation': row['date_deliberation'],
                'statut': row['statut'] or 'EN_ATTENTE'
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} délibérations transférées")

# 8. RECOURS
print("\n📮 Transfert des Recours...")
cursor.execute("SELECT * FROM core_recours")
count = 0
for row in cursor.fetchall():
    try:
        etudiant = Etudiant.objects.get(matricule_et=row['etudiant_id'])
        
        Recours.objects.update_or_create(
            code_recours=row['code_recours'],
            defaults={
                'etudiant': etudiant,
                'objet': row['objet'] or 'autre',
                'code_cours': row['code_cours'] or '',
                'description': row['description'] or '',
                'statut': row['statut'] or 'EN_ATTENTE',
                'date_soumission': row['date_soumission']
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} recours transférés")

# 9. COMMUNIQUÉS DÉLIBÉRATION
print("\n📢 Transfert des Communiqués Délibération...")
cursor.execute("SELECT * FROM core_communiquedeliberation")
count = 0
for row in cursor.fetchall():
    try:
        classe = Classe.objects.get(code_classe=row['code_classe_id'])
        
        CommuniqueDeliberation.objects.update_or_create(
            code_classe=classe,
            annee_academique=row['annee_academique'],
            date_deliberation=row['date_deliberation'],
            defaults={
                'message': row['message'] or '',
                'publie': bool(row['publie'])
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} communiqués transférés")

# 10. COMMENTAIRES COURS
print("\n💬 Transfert des Commentaires Cours...")
cursor.execute("SELECT * FROM core_commentairecours")
count = 0
for row in cursor.fetchall():
    try:
        etudiant = Etudiant.objects.get(matricule_et=row['etudiant_id'])
        
        CommentaireCours.objects.update_or_create(
            etudiant=etudiant,
            code_cours=row['code_cours'],
            type_cours=row['type_cours'],
            defaults={
                'commentaire': row['commentaire'] or '',
                'date_commentaire': row['date_commentaire']
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} commentaires transférés")

# 11. ÉVALUATIONS ENSEIGNEMENT
print("\n⭐ Transfert des Évaluations Enseignement...")
cursor.execute("SELECT * FROM core_evaluationenseignement")
count = 0
for row in cursor.fetchall():
    try:
        etudiant = Etudiant.objects.get(matricule_et=row['etudiant_id'])
        enseignant = Enseignant.objects.get(matricule_en=row['enseignant_id'])
        
        EvaluationEnseignement.objects.update_or_create(
            etudiant=etudiant,
            enseignant=enseignant,
            code_cours=row['code_cours'],
            defaults={
                'note_contenu': row['note_contenu'] or 3,
                'note_pedagogie': row['note_pedagogie'] or 3,
                'note_disponibilite': row['note_disponibilite'] or 3,
                'note_ponctualite': row['note_ponctualite'] or 3,
                'commentaire': row['commentaire'] or '',
                'date_evaluation': row['date_evaluation']
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} évaluations enseignement transférées")

# 12. PARAMÈTRES ÉVALUATION
print("\n⚙️ Transfert des Paramètres Évaluation...")
cursor.execute("SELECT * FROM core_parametreevaluation")
count = 0
for row in cursor.fetchall():
    try:
        classe = Classe.objects.get(code_classe=row['code_classe_id'])
        
        ParametreEvaluation.objects.update_or_create(
            code_classe=classe,
            annee_academique=row['annee_academique'],
            defaults={
                'rattrapage_actif': bool(row['rattrapage_actif']),
                'rachat_actif': bool(row['rachat_actif'])
            }
        )
        count += 1
    except:
        pass
print(f"  ✓ {count} paramètres transférés")

conn.close()

print("\n" + "=" * 70)
print("✅ TRANSFERT DE TOUTES LES TABLES MANQUANTES TERMINÉ!")

# Résumé complet
print("\n📊 RÉSUMÉ COMPLET:")
print(f"  • Utilisateurs: {User.objects.count()}")
print(f"  • Content Types: {ContentType.objects.count()}")
print(f"  • Permissions: {Permission.objects.count()}")
print(f"  • Cours Attributions: {CoursAttribution.objects.count()}")
print(f"  • Attributions: {Attribution.objects.count()}")
print(f"  • Bulletins: {BulletinNotes.objects.count()}")
print(f"  • Délibérations: {Deliberation.objects.count()}")
print(f"  • Recours: {Recours.objects.count()}")
print(f"  • Communiqués: {CommuniqueDeliberation.objects.count()}")
print(f"  • Commentaires: {CommentaireCours.objects.count()}")
print(f"  • Évaluations Enseignement: {EvaluationEnseignement.objects.count()}")
print(f"  • Paramètres Évaluation: {ParametreEvaluation.objects.count()}")
