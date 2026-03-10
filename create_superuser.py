#!/usr/bin/env python
"""Script pour créer un super utilisateur sur cPanel."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Modifiez ces valeurs selon vos besoins
ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@lmdmanagerpro.com'
ADMIN_PASSWORD = 'Admin@2026!'

if User.objects.filter(username=ADMIN_USERNAME).exists():
    print(f"L'utilisateur '{ADMIN_USERNAME}' existe déjà.")
else:
    user = User.objects.create_superuser(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
    )
    print(f"Super utilisateur '{ADMIN_USERNAME}' créé avec succès!")
    print(f"Mot de passe: {ADMIN_PASSWORD}")
    print("⚠ CHANGEZ CE MOT DE PASSE après la première connexion!")
