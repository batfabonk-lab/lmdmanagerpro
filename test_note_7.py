import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from core.models import Etudiant, Classe
from core.utils_profil_pdf import recuperer_donnees_profil

# Récupérer l'étudiant ETU001
etudiant = Etudiant.objects.get(matricule_et='ETU001')
classe = Classe.objects.first()

# Appeler la fonction
donnees = recuperer_donnees_profil(etudiant, classe, None, None)

print('=' * 80)
print('VERIFICATION: EC avec note <= 7')
print('=' * 80)

for row in donnees['rows']:
    note = row['note']
    if note is not None and note <= 7:
        print(f"Code: {row['code_ec']}")
        print(f"Intitulé: {row['intitule_ec'][:50]}")
        print(f"Note: {note:.2f}")
        print(f"Statut: {row['statut']}")
        print(f"Compensé: {row.get('compensated', False)}")
        print(f"Crédit compté dans capitalisés: {'OUI' if (note >= 10 or (note > 7 and row.get('compensated', False))) else 'NON'}")
        print('-' * 80)

print('\n' + '=' * 80)
print('VERIFICATION: EC avec note entre 8 et 9')
print('=' * 80)

for row in donnees['rows']:
    note = row['note']
    if note is not None and 8 <= note < 10:
        print(f"Code: {row['code_ec']}")
        print(f"Intitulé: {row['intitule_ec'][:50]}")
        print(f"Note: {note:.2f}")
        print(f"Statut: {row['statut']}")
        print(f"Compensé: {row.get('compensated', False)}")
        print(f"Crédit compté dans capitalisés: {'OUI' if (note >= 10 or (note > 7 and row.get('compensated', False))) else 'NON'}")
        print('-' * 80)

print(f"\nCrédits totaux: {donnees['credits_total']}")
print(f"Crédits validés: {donnees['credits_valides']}")
