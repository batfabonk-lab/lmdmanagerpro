import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanager.settings')
django.setup()

from core.models import Deliberation, Etudiant, UE

print("=== TEST LOGIQUE SIMPLE ===\n")

etudiant = Etudiant.objects.get(matricule_et='ETU001')
annee = '2025-2026'
type_deliberation = 'S1'

# Récupérer les délibérations
deliberations = Deliberation.objects.filter(
    matricule_etudiant=etudiant,
    type_deliberation=type_deliberation,
    annee_academique=annee
).select_related('code_ue', 'code_ec', 'code_ec__code_ue')

# Regrouper par UE
ue_data = {}

for delib in deliberations:
    if delib.code_ec and delib.code_ec.code_ue:
        ue = delib.code_ec.code_ue
        ue_code = ue.code_ue
    elif delib.code_ue:
        ue = delib.code_ue
        ue_code = ue.code_ue
    else:
        continue
    
    if ue_code not in ue_data:
        ue_data[ue_code] = {
            'ue': ue,
            'deliberations': []
        }
    
    ue_data[ue_code]['deliberations'].append(delib)

# Test logique proportionnelle
print("LOGIQUE PROPORTIONNELLE:")
total_prop = 0
for ue_code, data in ue_data.items():
    ue = data['ue']
    statuts_ec = [delib.statut for delib in data['deliberations']]
    nb_valides = sum(1 for statut in statuts_ec if statut == 'VALIDE')
    proportion = nb_valides / len(statuts_ec)
    credits_prop = ue.credit * proportion
    
    total_prop += credits_prop
    print(f"UE {ue_code}: {credits_prop:.1f} credits ({nb_valides}/{len(statuts_ec)} EC valides)")

print(f"Total: {total_prop:.1f} credits")

# Test logique seuil 25%
print("\nLOGIQUE SEUIL 25%:")
total_seuil25 = 0
for ue_code, data in ue_data.items():
    ue = data['ue']
    statuts_ec = [delib.statut for delib in data['deliberations']]
    nb_valides = sum(1 for statut in statuts_ec if statut == 'VALIDE')
    proportion = nb_valides / len(statuts_ec)
    
    if proportion >= 0.25:
        total_seuil25 += ue.credit
        print(f"UE {ue_code}: {ue.credit} credits (>=25% EC valides)")
    else:
        print(f"UE {ue_code}: 0 credits (<25% EC valides)")

print(f"Total: {total_seuil25} credits")

print(f"\nAttendu (UI): 20 credits")
print(f"Proportionnel: {total_prop:.1f} credits")
print(f"Seuil 25%: {total_seuil25} credits")
