import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanager.settings')
django.setup()

from core.models import Deliberation, Etudiant, UE

print("=== TEST DE LA FONCTION ÉTAPE PAR ÉTAPE ===\n")

etudiant = Etudiant.objects.get(matricule_et='ETU001')
annee = '2024-2025'
type_deliberation = 'S1'

# Récupérer les délibérations exactement comme dans la fonction
deliberations = Deliberation.objects.filter(
    matricule_etudiant=etudiant,
    type_deliberation=type_deliberation,
    annee_academique=annee
).select_related('code_ue', 'code_ec', 'code_ec__code_ue')

print(f"Nombre de délibérations: {deliberations.count()}")

# Regrouper par UE exactement comme dans la fonction
ue_data = {}

for delib in deliberations:
    print(f"\nTraitement délibération ID: {delib.id_delib}")
    
    # Calculer la note finale
    note_finale = delib.calculer_note_finale()
    print(f"Note finale: {note_finale}")
    
    # Déterminer l'UE
    if delib.code_ec and delib.code_ec.code_ue:
        ue = delib.code_ec.code_ue
        ue_code = ue.code_ue
        print(f"UE trouvée via EC: {ue_code}")
    elif delib.code_ue:
        ue = delib.code_ue
        ue_code = ue.code_ue
        print(f"UE trouvée directement: {ue_code}")
    else:
        print("Aucune UE trouvée - SKIP")
        continue
    
    # Initialiser l'UE si pas encore faite
    if ue_code not in ue_data:
        print(f"Initialisation UE {ue_code}")
        ue_data[ue_code] = {
            'code_ue': ue_code,
            'intitule_ue': ue.intitule_ue,
            'categorie': getattr(ue, 'categorie', ''),
            'credit_ue': ue.credit or 0,
            'deliberations': []
        }
        print(f"  - Crédits: {ue_data[ue_code]['credit_ue']}")
    
    # Ajouter la délibération
    ue_data[ue_code]['deliberations'].append({
        'code_ec': delib.code_ec.code_ec if delib.code_ec else ue_code,
        'intitule_ec': delib.code_ec.intitule_ue if delib.code_ec else '-',
        'cc': delib.cc,
        'examen': delib.examen,
        'note': note_finale,
        'rattrapage': delib.rattrapage,
        'statut': delib.statut
    })
    print(f"  - Délibération ajoutée, total: {len(ue_data[ue_code]['deliberations'])}")

print(f"\n=== RÉSUMÉ UE DATA ===")
print(f"Nombre d'UE: {len(ue_data)}")

credits_total = 0
for ue_code, data in ue_data.items():
    credit = data['credit_ue']
    credits_total += credit
    print(f"UE {ue_code}: {credit} crédits")

print(f"\nTotal crédits: {credits_total}")

# Maintenant testons les calculs de statistiques
credits_total = 0
credits_valides = 0
total_points = 0
total_credits = 0

categories_points = {'A': 0, 'B': 0}
categories_credits = {'A': 0, 'B': 0}

for ue_code, data in ue_data.items():
    print(f"\nCalculs pour UE {ue_code}:")
    
    # Calculer la moyenne de l'UE
    notes_ec = [d['note'] for d in data['deliberations'] if d['note'] is not None]
    print(f"  Notes EC: {notes_ec}")
    moyenne_ue = sum(notes_ec) / len(notes_ec) if notes_ec else None
    print(f"  Moyenne UE: {moyenne_ue}")
    
    # Déterminer le statut de l'UE
    statut_ue = 'VALIDE' if any(d['statut'] == 'VALIDE' for d in data['deliberations']) else 'NON_VALIDE'
    print(f"  Statut UE: {statut_ue}")
    
    # Calculer les statistiques
    credits_total += data['credit_ue']
    print(f"  Credits total cumulé: {credits_total}")
    
    if statut_ue == 'VALIDE':
        credits_valides += data['credit_ue']
        print(f"  Credits validés cumulé: {credits_valides}")
    
    if moyenne_ue is not None:
        points_ue = moyenne_ue * data['credit_ue']
        total_points += points_ue
        total_credits += data['credit_ue']
        print(f"  Points UE: {points_ue}")
        
        # Ajouter aux catégories
        categorie = data['categorie']
        if categorie in categories_points:
            categories_points[categorie] += points_ue
            categories_credits[categorie] += data['credit_ue']
            print(f"  Catégorie {categorie}: points={categories_points[categorie]}, credits={categories_credits[categorie]}")

print(f"\n=== STATISTIQUES FINALES ===")
print(f"Total crédits: {credits_total}")
print(f"Crédits validés: {credits_valides}")

moyenne = total_points / total_credits if total_credits > 0 else None
moyenne_cat_a = categories_points['A'] / categories_credits['A'] if categories_credits['A'] > 0 else None
moyenne_cat_b = categories_points['B'] / categories_credits['B'] if categories_credits['B'] > 0 else None

print(f"Moyenne générale: {moyenne}")
print(f"Moyenne catégorie A: {moyenne_cat_a}")
print(f"Moyenne catégorie B: {moyenne_cat_b}")
