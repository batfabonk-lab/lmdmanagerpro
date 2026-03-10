#!/usr/bin/env python
"""Script de setup pour cPanel - exécute les migrations et collectstatic."""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command

print("=" * 50)
print("LMD Manager Pro - Setup cPanel")
print("=" * 50)

# 1. Migrations
print("\n[1/3] Exécution des migrations...")
try:
    call_command('migrate', verbosity=1)
    print("✓ Migrations terminées avec succès!")
except Exception as e:
    print(f"✗ Erreur lors des migrations: {e}")

# 2. Collectstatic
print("\n[2/3] Collecte des fichiers statiques...")
try:
    call_command('collectstatic', '--noinput', verbosity=1)
    print("✓ Fichiers statiques collectés!")
except Exception as e:
    print(f"✗ Erreur lors de collectstatic: {e}")

# 3. Vérification
print("\n[3/3] Vérification...")
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    count = User.objects.count()
    print(f"✓ Base de données OK - {count} utilisateur(s) trouvé(s)")
    if count == 0:
        print("\n⚠ Aucun utilisateur trouvé!")
        print("Pour créer un super utilisateur, exécutez:")
        print("  python create_superuser.py")
except Exception as e:
    print(f"✗ Erreur: {e}")

print("\n" + "=" * 50)
print("Setup terminé!")
print("=" * 50)
