import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanager.settings')
django.setup()

from core.models import Etudiant
from core.utils_profil_pdf_simple import recuperer_donnees_deliberation
from core.utils_releve_pdf_simple import recuperer_donnees_deliberation_releve

print("=== TEST DES NOUVELLES FONCTIONS PDF ===\n")

# Récupérer l'étudiant ETU001
etudiant = Etudiant.objects.get(matricule_et='ETU001')
annee = '2024-2025'
type_deliberation = 'S1'

print("=== FONCTION PROFIL PDF ===")
donnees_profil = recuperer_donnees_deliberation(etudiant, type_deliberation, annee)

print(f"Total crédits: {donnees_profil['credits_total']}")
print(f"Crédits validés: {donnees_profil['credits_valides']}")
print(f"Moyenne générale: {donnees_profil['moyenne']:.2f}" if donnees_profil['moyenne'] else "Moyenne générale: N/A")
print(f"Moyenne catégorie A: {donnees_profil['moyenne_cat_a']:.2f}" if donnees_profil['moyenne_cat_a'] else "Moyenne catégorie A: N/A")
print(f"Moyenne catégorie B: {donnees_profil['moyenne_cat_b']:.2f}" if donnees_profil['moyenne_cat_b'] else "Moyenne catégorie B: N/A")

print("\nDétail des lignes:")
for row in donnees_profil['rows']:
    if row['credit'] > 0:  # Afficher seulement les lignes avec crédits (première ligne de chaque UE)
        print(f"UE: {row['code_ue']} - {row['intitule_ue']}")
        print(f"  EC: {row['code_ec']} - {row['intitule_ec']}")
        print(f"  Catégorie: {row['categorie']}, Crédits: {row['credit']}")
        print(f"  Note: {row['note']}, Statut: {row['statut']}")
        print("-" * 40)

print("\n" + "="*60 + "\n")

print("=== FONCTION RELEVÉ PDF ===")
donnees_releve = recuperer_donnees_deliberation_releve(etudiant, type_deliberation, annee)

print(f"Total crédits: {donnees_releve['credits_total']}")
print(f"Crédits capitalisés: {donnees_releve['credits_capitalises']}")
print(f"Crédits non capitalisés: {donnees_releve['credits_non_capitalises']}")
print(f"Pourcentage: {donnees_releve['pourcentage']:.1f}%")
print(f"Moyenne générale: {donnees_releve['moyenne']:.2f}" if donnees_releve['moyenne'] else "Moyenne générale: N/A")
print(f"Moyenne catégorie A: {donnees_releve['moyenne_cat_a']:.2f}" if donnees_releve['moyenne_cat_a'] else "Moyenne catégorie A: N/A")
print(f"Moyenne catégorie B: {donnees_releve['moyenne_cat_b']:.2f}" if donnees_releve['moyenne_cat_b'] else "Moyenne catégorie B: N/A")
print(f"Décision: {donnees_releve['decision']}")

print("\nDétail des lignes:")
for row in donnees_releve['rows']:
    if row['credit_ue'] > 0:  # Afficher seulement les lignes avec crédits (première ligne de chaque UE)
        print(f"UE: {row['code_ue']} - {row['intitule_ue']}")
        print(f"  EC: {row['elements_constitutifs']}")
        print(f"  Catégorie: {row['categorie_ec']}, Crédits: {row['credit_ue']}")
        print(f"  Moyenne UE: {row['moyenne']:.2f}" if row['moyenne'] else "Moyenne UE: N/A")
        print(f"  Statut: {row['statut']}")
        print("-" * 40)

print("\n=== COMPARAISON AVEC L'UI ===")
print("Attendu (UI): Total=30, Capitalisés=20, Taux=66.7%")
print(f"Profil PDF: Total={donnees_profil['credits_total']}, Validés={donnees_profil['credits_valides']}")
print(f"Relevé PDF: Total={donnees_releve['credits_total']}, Capitalisés={donnees_releve['credits_capitalises']}, Taux={donnees_releve['pourcentage']:.1f}%")

print("\n=== TEST TERMINÉ ===")
