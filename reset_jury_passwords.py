#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanager.settings')
django.setup()

from core.models import User

# Réinitialiser les mots de passe des comptes jury
try:
    # Président jury
    president = User.objects.get(username='jury_pres_MAT008')
    president.set_password('password')
    president.save()
    print("Mot de passe du président jury réinitialisé: password")
except User.DoesNotExist:
    print("Compte président jury non trouvé")

try:
    # Secrétaire jury
    secretary = User.objects.get(username='jury_sec_MAT007')
    secretary.set_password('password')
    secretary.save()
    print("Mot de passe du secrétaire jury réinitialisé: password")
except User.DoesNotExist:
    print("Compte secrétaire jury non trouvé")

print("\nTous les comptes jury ont maintenant le mot de passe: password")
