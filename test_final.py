import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanager.settings')
django.setup()

from core.models import Etudiant
from core.utils_profil_pdf_simple import recuperer_donnees_deliberation
from core.utils_releve_pdf_simple import recuperer_donnees_deliberation_releve

print("=== TEST FINAL AVEC BONNE ANNÉE ===\n")

etudiant = Etudiant.objects.get(matricule_et='ETU001')
annee = '2025-2026'
type_deliberation = 'S1'

print("=== FONCTION PROFIL PDF ===")
donnees_profil = recuperer_donnees_deliberation(etudiant, type_deliberation, annee)

print(f"Total crédits: {donnees_profil['credits_total']}")
print(f"Crédits validés: {donnees_profil['credits_valides']}")
print(f"Moyenne générale: {donnees_profil['moyenne']:.2f}" if donnees_profil['moyenne'] else "Moyenne générale: N/A")
print(f"Moyenne catégorie A: {donnees_profil['moyenne_cat_a']:.2f}" if donnees_profil['moyenne_cat_a'] else "Moyenne catégorie A: N/A")
print(f"Moyenne catégorie B: {donnees_profil['moyenne_cat_b']:.2f}" if donnees_profil['moyenne_cat_b'] else "Moyenne catégorie B: N/A")

print("\n=== FONCTION RELEVÉ PDF ===")
donnees_releve = recuperer_donnees_deliberation_releve(etudiant, type_deliberation, annee)

print(f"Total crédits: {donnees_releve['credits_total']}")
print(f"Crédits capitalisés: {donnees_releve['credits_capitalises']}")
print(f"Pourcentage: {donnees_releve['pourcentage']:.1f}%")
print(f"Moyenne générale: {donnees_releve['moyenne']:.2f}" if donnees_releve['moyenne'] else "Moyenne générale: N/A")
print(f"Moyenne catégorie A: {donnees_releve['moyenne_cat_a']:.2f}" if donnees_releve['moyenne_cat_a'] else "Moyenne catégorie A: N/A")
print(f"Moyenne catégorie B: {donnees_releve['moyenne_cat_b']:.2f}" if donnees_releve['moyenne_cat_b'] else "Moyenne catégorie B: N/A")
print(f"Décision: {donnees_releve['decision']}")

print("\n=== COMPARAISON AVEC L'UI ===")
print("Attendu (UI): Total=30, Capitalisés=20, Taux=66.7%")
print(f"Profil PDF: Total={donnees_profil['credits_total']}, Validés={donnees_profil['credits_valides']}")
print(f"Relevé PDF: Total={donnees_releve['credits_total']}, Capitalisés={donnees_releve['credits_capitalises']}, Taux={donnees_releve['pourcentage']:.1f}%")

# Vérifier les statuts individuels
print("\n=== STATUTS INDIVIDUELS ===")
for row in donnees_profil['rows']:
    if row['credit'] > 0:  # Seulement les lignes avec crédits
        print(f"{row['code_ec']}: {row['statut']}")

print("\n=== TEST TERMINÉ ===")
