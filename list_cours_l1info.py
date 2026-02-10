import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanager.settings')
django.setup()

from core.models import Attribution, CoursAttribution
from reglage.models import Classe

try:
    classe = Classe.objects.get(code_classe='L1INFO')
    print(f"Classe trouvée: {classe}\n")
    
    cours_attribution = CoursAttribution.objects.filter(classe=classe)
    
    print("=== COURS DANS ATTRIBUTION POUR L1INFO ===\n")
    print(f"{'Code':<15} | {'Intitulé':<50} | {'Crédits':<8} | {'Type':<5} | {'Semestre'}")
    print("-" * 100)
    
    total_credits = 0
    cours_list = []
    
    for cours in cours_attribution:
        print(f"{cours.code_cours:<15} | {cours.intitule:<50} | {cours.credit:<8} | {cours.type_cours:<5} | S{cours.semestre}")
        total_credits += cours.credit
        cours_list.append(cours)
    
    print("-" * 100)
    print(f"\n=== TOTAL: {len(cours_list)} cours | {total_credits} crédits ===\n")
    
    attributions = Attribution.objects.filter(
        code_cours__in=cours_attribution.values_list('code_cours', flat=True)
    ).select_related('matricule_en')
    
    if attributions.exists():
        print("\n=== ENSEIGNANTS ATTRIBUÉS ===\n")
        for attr in attributions:
            cours = cours_attribution.filter(code_cours=attr.code_cours).first()
            if cours:
                print(f"{attr.code_cours:<15} | {attr.matricule_en.nom_complet:<40} | {attr.annee_academique}")
    
except Classe.DoesNotExist:
    print("Erreur: La classe L1INFO n'existe pas dans la base de données")
except Exception as e:
    print(f"Erreur: {e}")
