import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanager.settings')
django.setup()

from core.models import Deliberation, Etudiant, UE
from django.db.models import Sum, Avg, Q

print("=== Requête de délibération pour ETU001 - S1 ===\n")

# Récupérer l'étudiant ETU001
try:
    etudiant = Etudiant.objects.get(matricule='ETU001')
    print(f"Étudiant trouvé: {etudiant.nom} {etudiant.postnom} {etudiant.prenom}")
except Etudiant.DoesNotExist:
    print("Étudiant ETU001 non trouvé")
    exit()

# Récupérer toutes les délibérations pour cet étudiant avec type S1
deliberations = Deliberation.objects.filter(
    matricule_etudiant=etudiant,
    type_deliberation='S1'
)

print(f"\nNombre de délibérations trouvées: {deliberations.count()}")

if deliberations.exists():
    # Calculer la somme des crédits totaux
    credits_total = deliberations.aggregate(
        total=Sum('code_ue__credit')
    )['total'] or 0
    
    # Calculer la somme des crédits capitalisés (statut VALIDé)
    credits_capitalises = deliberations.filter(
        statut='VALIDE'
    ).aggregate(
        total=Sum('code_ue__credit')
    )['total'] or 0
    
    # Calculer la moyenne générale (pondérée par les crédits)
    total_points = 0
    total_credits = 0
    
    for delib in deliberations:
        note_finale = delib.calculer_note_finale()
        if note_finale is not None and delib.code_ue and delib.code_ue.credit:
            total_points += note_finale * delib.code_ue.credit
            total_credits += delib.code_ue.credit
    
    moyenne_generale = total_points / total_credits if total_credits > 0 else 0
    
    # Calculer les moyennes par catégorie
    categories = {}
    for delib in deliberations:
        note_finale = delib.calculer_note_finale()
        if note_finale is not None and delib.code_ue:
            categorie = delib.code_ue.categorie if hasattr(delib.code_ue, 'categorie') and delib.code_ue.categorie else 'Non définie'
            credit = delib.code_ue.credit if delib.code_ue.credit else 0
            
            if categorie not in categories:
                categories[categorie] = {'total_points': 0, 'total_credits': 0}
            
            categories[categorie]['total_points'] += note_finale * credit
            categories[categorie]['total_credits'] += credit
    
    # Afficher les résultats
    print(f"\n=== RÉSULTATS POUR {etudiant.matricule} - S1 ===")
    print(f"Somme des crédits totaux: {credits_total}")
    print(f"Somme des crédits capitalisés: {credits_capitalises}")
    print(f"Moyenne générale: {moyenne_generale:.2f}")
    
    print(f"\nMoyennes par catégorie:")
    for categorie, data in categories.items():
        moyenne_categorie = data['total_points'] / data['total_credits'] if data['total_credits'] > 0 else 0
        print(f"  - {categorie}: {moyenne_categorie:.2f} ({data['total_credits']} crédits)")
    
    # Afficher le détail des délibérations
    print(f"\nDétail des délibérations:")
    for delib in deliberations:
        note_finale = delib.calculer_note_finale()
        categorie = delib.code_ue.categorie if hasattr(delib.code_ue, 'categorie') and delib.code_ue.categorie else 'Non définie'
        print(f"  - {delib.code_ue.code_ue}: CC={delib.cc}, Exam={delib.examen}, Note={note_finale}, Crédits={delib.code_ue.credit}, Catégorie={categorie}, Statut={delib.statut}")
        
else:
    print("Aucune délibération trouvée pour ETU001 avec type S1")

print("\n=== Requête terminée ===")
