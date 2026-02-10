import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanager.settings')
django.setup()

from core.models import Deliberation, Etudiant, UE

print("=== TEST LOGIQUE DE CAPITALISATION PARTIELLE ===\n")

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

print("ANALYSE AVEC DIFFÉRENTES LOGIQUES:")

# Logique 1: Tous les EC validés = 100% des crédits
print("\n1. LOGIQUE STRICTE (tous validés = 100%):")
total_strict = 0
for ue_code, data in ue_data.items():
    ue = data['ue']
    statuts_ec = [delib.statut for delib in data['deliberations']]
    tous_valides = all(statut == 'VALIDE' for statut in statuts_ec)
    
    if tous_valides:
        total_strict += ue.credit
        print(f"  {ue_code}: {ue.credit} crédits (100%)")
    else:
        print(f"  {ue_code}: 0 crédits (tous non validés)")

print(f"  Total: {total_strict} crédits")

# Logique 2: Proportionnelle au nombre d'EC validés
print("\n2. LOGIQUE PROPORTIONNELLE (% d'EC validés):")
total_prop = 0
for ue_code, data in ue_data.items():
    ue = data['ue']
    statuts_ec = [delib.statut for delib in data['deliberations']]
    nb_valides = sum(1 for statut in statuts_ec if statut == 'VALIDE')
    proportion = nb_valides / len(statuts_ec)
    credits_prop = ue.credit * proportion
    
    total_prop += credits_prop
    print(f"  {ue_code}: {credits_prop:.1f} crédits ({nb_valides}/{len(statuts_ec)} EC validés = {proportion*100:.1f}%)")

print(f"  Total: {total_prop:.1f} crédits")

# Logique 3: Seuil de 50% des EC validés = 100% des crédits
print("\n3. LOGIQUE SEUIL 50% (>=50% EC validés = 100%):")
total_seuil = 0
for ue_code, data in ue_data.items():
    ue = data['ue']
    statuts_ec = [delib.statut for delib in data['deliberations']]
    nb_valides = sum(1 for statut in statuts_ec if statut == 'VALIDE')
    proportion = nb_valides / len(statuts_ec)
    
    if proportion >= 0.5:
        total_seuil += ue.credit
        print(f"  {ue_code}: {ue.credit} crédits (>=50% EC validés)")
    else:
        print(f"  {ue_code}: 0 crédits (<50% EC validés)")

print(f"  Total: {total_seuil} crédits")

# Logique 4: Seuil de 25% des EC validés = 100% des crédits
print("\n4. LOGIQUE SEUIL 25% (>=25% EC validés = 100%):")
total_seuil25 = 0
for ue_code, data in ue_data.items():
    ue = data['ue']
    statuts_ec = [delib.statut for delib in data['deliberations']]
    nb_valides = sum(1 for statut in statuts_ec if statut == 'VALIDE')
    proportion = nb_valides / len(statuts_ec)
    
    if proportion >= 0.25:
        total_seuil25 += ue.credit
        print(f"  {ue_code}: {ue.credit} crédits (>=25% EC validés)")
    else:
        print(f"  {ue_code}: 0 crédits (<25% EC validés)")

print(f"  Total: {total_seuil25} crédits")

print(f"\nRÉSUMÉ:")
print(f"Attendu (UI): 20 crédits")
print(f"Logique stricte: {total_strict} crédits")
print(f"Logique proportionnelle: {total_prop:.1f} crédits")
print(f"Logique seuil 50%: {total_seuil} crédits")
print(f"Logique seuil 25%: {total_seuil25} crédits")

if abs(total_prop - 20) < 0.1:
    print(f"\n✅ La logique proportionnelle correspond à l'UI!")
elif total_seuil == 20:
    print(f"\n✅ La logique seuil 50% correspond à l'UI!")
elif total_seuil25 == 20:
    print(f"\n✅ La logique seuil 25% correspond à l'UI!")
else:
    print(f"\n❌ Aucune logique ne correspond exactement à l'UI")
