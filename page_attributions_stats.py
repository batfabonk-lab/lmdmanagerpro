import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
import django
django.setup()

from core.models import Attribution, UE, EC, Enseignant
from reglage.models import AnneeAcademique, Classe

print('=== STATISTIQUES PAGE ATTRIBUTIONS ===\n')

# Récupérer toutes les attributions (pas de filtre)
attributions = Attribution.objects.all().select_related('matricule_en', 'type_charge').order_by('-date_attribution')

print(f"Total d'attributions: {attributions.count()}\n")

# Calculer le total des crédits
total_credits = 0
total_attributions = 0
attributions_par_classe = {}

for attr in attributions:
    total_attributions += 1
    
    # Chercher dans UE
    try:
        ue = UE.objects.get(code_ue=attr.code_cours)
        total_credits += ue.credit
        classe = ue.classe
    except UE.DoesNotExist:
        # Chercher dans EC
        try:
            ec = EC.objects.get(code_ec=attr.code_cours)
            total_credits += ec.credit
            classe = ec.classe
        except EC.DoesNotExist:
            classe = None
    
    # Compter par classe
    if classe:
        classe_code = classe.code_classe
        if classe_code not in attributions_par_classe:
            attributions_par_classe[classe_code] = {'count': 0, 'credits': 0}
        attributions_par_classe[classe_code]['count'] += 1
        try:
            ue = UE.objects.get(code_ue=attr.code_cours)
            attributions_par_classe[classe_code]['credits'] += ue.credit
        except:
            try:
                ec = EC.objects.get(code_ec=attr.code_cours)
                attributions_par_classe[classe_code]['credits'] += ec.credit
            except:
                pass

print("=== STATISTIQUES GLOBALES ===")
print(f"Total attributions: {total_attributions}")
print(f"Total crédits: {total_credits}")
print(f"Nombre d'enseignants: {Enseignant.objects.count()}")
print(f"Nombre de classes: {Classe.objects.count()}")
print(f"Nombre d'années académiques: {AnneeAcademique.objects.count()}")

print("\n=== PAR CLASSE ===")
for classe_code in sorted(attributions_par_classe.keys()):
    data = attributions_par_classe[classe_code]
    print(f"{classe_code}: {data['count']} attributions | {data['credits']} crédits")

print("\n=== PAR ENSEIGNANT (TOP 10) ===")
from collections import Counter
enseignants_count = Counter(attributions.values_list('matricule_en__nom_complet', flat=True))
for enseignant, count in enseignants_count.most_common(10):
    print(f"{enseignant}: {count} attributions")
