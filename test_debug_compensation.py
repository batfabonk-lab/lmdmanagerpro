import os
import sys
import django

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from core.models import Etudiant, Classe, Evaluation, EC, UE
from django.db.models import Q

# Récupérer l'étudiant ETU001
etudiant = Etudiant.objects.get(matricule_et='ETU001')

# Récupérer toutes les évaluations
evaluations = Evaluation.objects.filter(
    matricule_etudiant=etudiant,
    statut__in=['VALIDE', 'NON_VALIDE']
).select_related(
    'code_ue',
    'code_ec',
    'code_ec__code_ue'
)

print('=' * 80)
print('STRUCTURE DES UE ET EC')
print('=' * 80)

# Regrouper par UE
ue_tableau = {}

for ev in evaluations:
    if ev.code_ec and ev.code_ec.code_ue:
        ec = ev.code_ec
        ue = ec.code_ue
        
        if ue.code_ue not in ue_tableau:
            ue_tableau[ue.code_ue] = {
                'ue': ue,
                'categorie': ue.categorie,
                'ec_list': []
            }
        
        cc = ev.cc if ev.cc is not None else None
        examen = ev.examen if ev.examen is not None else None
        note = (cc + examen) if (cc is not None and examen is not None) else None
        
        ue_tableau[ue.code_ue]['ec_list'].append({
            'code_ec': ec.code_ec,
            'intitule': ec.intitule_ue,
            'note': note
        })

# Afficher la structure
for code_ue, data in sorted(ue_tableau.items()):
    print(f"\nUE: {code_ue} - Catégorie: {data['categorie']}")
    print(f"  EC dans cette UE:")
    for ec in data['ec_list']:
        print(f"    - {ec['code_ec']}: {ec['intitule'][:40]:40} | Note: {ec['note']}")

print('\n' + '=' * 80)
print('VERIFICATION: TCI127_b appartient à quelle UE?')
print('=' * 80)

# Chercher TCI127_b
for code_ue, data in ue_tableau.items():
    for ec in data['ec_list']:
        if ec['code_ec'] == 'TCI127_b':
            print(f"TCI127_b appartient à l'UE: {code_ue}")
            print(f"Catégorie: {data['categorie']}")
            print(f"Autres EC de cette UE:")
            for other_ec in data['ec_list']:
                if other_ec['code_ec'] != 'TCI127_b':
                    print(f"  - {other_ec['code_ec']}: Note {other_ec['note']}")
