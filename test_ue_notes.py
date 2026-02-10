import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from core.models import Etudiant, Evaluation
from django.db.models import Q

etudiant = Etudiant.objects.get(matricule_et='ETU001')

evaluations = Evaluation.objects.filter(
    matricule_etudiant=etudiant,
    statut__in=['VALIDE', 'NON_VALIDE']
).select_related('code_ue', 'code_ec', 'code_ec__code_ue')

# Regrouper par UE et calculer les moyennes
ue_dict = {}

for ev in evaluations:
    if ev.code_ec and ev.code_ec.code_ue:
        ue = ev.code_ec.code_ue
        if ue.code_ue not in ue_dict:
            ue_dict[ue.code_ue] = {
                'ue': ue,
                'evaluations': []
            }
        ue_dict[ue.code_ue]['evaluations'].append(ev)

# Calculer les notes moyennes par UE
ue_notes = {}
for code_ue, data in ue_dict.items():
    ue = data['ue']
    evals = data['evaluations']
    
    notes_ue = []
    for ev in evals:
        if ev.cc is not None and ev.examen is not None:
            note = ev.cc + ev.examen
            notes_ue.append(note)
    
    if notes_ue:
        ue_notes[code_ue] = sum(notes_ue) / len(notes_ue)

print('=' * 80)
print('NOTES MOYENNES PAR UE')
print('=' * 80)
for code_ue, note_ue in sorted(ue_notes.items()):
    ue = ue_dict[code_ue]['ue']
    print(f"{code_ue}: {note_ue:6.2f} - Catégorie: {ue.categorie}")

print('\n' + '=' * 80)
print('VERIFICATION COMPENSATION INTER-UE (Catégorie A)')
print('=' * 80)

# Catégorie A
fails_ue = []
donors_ue = []

for code_ue, note_ue in ue_notes.items():
    ue = ue_dict[code_ue]['ue']
    if ue.categorie != 'A':
        continue
    
    print(f"{code_ue}: {note_ue:6.2f}", end='')
    
    if 8 <= note_ue < 10:
        fails_ue.append((code_ue, note_ue))
        print(" -> EN ECHEC (8-9)")
    elif note_ue > 10:
        donors_ue.append((code_ue, note_ue))
        print(f" -> DONATEUR (excès: {note_ue - 10:.2f})")
    else:
        print(" -> Hors compensation")

print(f"\nUE en échec: {fails_ue}")
print(f"UE donatrices: {donors_ue}")

# Vérifier TCI127
if 'TCI127' in ue_notes:
    note_tci127 = ue_notes['TCI127']
    print(f"\nTCI127 note moyenne: {note_tci127:.2f}")
    if 8 <= note_tci127 < 10:
        print("TCI127 est éligible à la compensation (8-9)")
    else:
        print("TCI127 n'est PAS éligible à la compensation")
