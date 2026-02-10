import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanager.settings')
django.setup()

from core.models import Deliberation, Etudiant
from django.db.models import Sum, Avg

print("=== VÉRIFICATION DES DONNÉES DELIBERATION POUR ETU001 - S1 ===\n")

# Récupérer l'étudiant ETU001
etudiant = Etudiant.objects.get(matricule_et='ETU001')
print(f"Étudiant: {etudiant.nom_complet}")

# Récupérer toutes les délibérations S1
deliberations = Deliberation.objects.filter(
    matricule_etudiant=etudiant,
    type_deliberation='S1'
).select_related('code_ue', 'code_ec').order_by('code_ue__code_ue', 'code_ec__code_ec')

print(f"\nNombre de délibérations: {deliberations.count()}")

# Afficher le détail de chaque délibération
print("\n=== DÉTAIL DES DÉLIBÉRATIONS ===")
for delib in deliberations:
    note_finale = delib.calculer_note_finale()
    credit = delib.code_ue.credit if delib.code_ue else 0
    categorie = getattr(delib.code_ue, 'categorie', '') if delib.code_ue else ''
    
    print(f"Code UE: {delib.code_ue.code_ue if delib.code_ue else 'N/A'}")
    print(f"Code EC: {delib.code_ec.code_ec if delib.code_ec else delib.code_ue.code_ue if delib.code_ue else 'N/A'}")
    print(f"Intitulé UE: {delib.code_ue.intitule_ue if delib.code_ue else 'N/A'}")
    print(f"Intitulé EC: {delib.code_ec.intitule_ue if delib.code_ec else 'N/A'}")
    print(f"Catégorie: {categorie}")
    print(f"Crédits: {credit}")
    print(f"CC: {delib.cc}")
    print(f"Examen: {delib.examen}")
    print(f"Note finale: {note_finale}")
    print(f"Statut: {delib.statut}")
    print("-" * 50)

# Calculer les statistiques
print("\n=== CALCULS STATISTIQUES ===")

# Total crédits
credits_total = sum(d.code_ue.credit for d in deliberations if d.code_ue)
print(f"Total crédits: {credits_total}")

# Crédits capitalisés
credits_capitalises = sum(d.code_ue.credit for d in deliberations 
                         if d.code_ue and d.statut == 'VALIDE')
print(f"Crédits capitalisés: {credits_capitalises}")

# Taux de capitalisation
taux = (credits_capitalises / credits_total * 100) if credits_total > 0 else 0
print(f"Taux capitalisation: {taux:.1f}%")

# Moyennes par catégorie
categories = {}
total_points = 0
total_credits = 0

for delib in deliberations:
    if delib.code_ue:
        note_finale = delib.calculer_note_finale()
        credit = delib.code_ue.credit
        categorie = getattr(delib.code_ue, 'categorie', '')
        
        if note_finale is not None and credit:
            total_points += note_finale * credit
            total_credits += credit
            
            if categorie not in categories:
                categories[categorie] = {'points': 0, 'credits': 0}
            categories[categorie]['points'] += note_finale * credit
            categories[categorie]['credits'] += credit

# Moyenne générale
moyenne_generale = total_points / total_credits if total_credits > 0 else 0
print(f"Moyenne générale: {moyenne_generale:.2f}")

# Moyennes par catégorie
for cat, data in categories.items():
    moy_cat = data['points'] / data['credits'] if data['credits'] > 0 else 0
    print(f"Moyenne catégorie {cat}: {moy_cat:.2f}")

print("\n=== VÉRIFICATION TERMINÉE ===")
