import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanager.settings')
django.setup()

from core.models import Deliberation, Evaluation, Etudiant, UE, EC
from django.contrib.auth.models import User

print("=== Test du modèle Deliberation ===\n")

# Vérifier le nombre de délibérations existantes
nb_deliberations = Deliberation.objects.count()
print(f"Nombre de délibérations existantes: {nb_deliberations}")

# Afficher les 5 premières délibérations si elles existent
deliberations = Deliberation.objects.all()[:5]
if deliberations:
    print("\nPremières délibérations:")
    for d in deliberations:
        print(f"  - {d}")
        print(f"    Type: {d.type_deliberation}, Année: {d.annee_academique}, Semestre: {d.semestre}")
        print(f"    Statut: {d.statut}, CC: {d.cc}, Examen: {d.examen}")
        print(f"    Créée par: {d.cree_par}, le: {d.date_creation}")
        print()
else:
    print("Aucune délibération trouvée")

# Vérifier la structure du modèle
print("\n=== Structure du modèle Deliberation ===")
for field in Deliberation._meta.fields:
    print(f"  - {field.name}: {field.__class__.__name__} ({field.verbose_name})")

# Test de création d'une délibération depuis une évaluation
print("\n=== Test de création depuis une évaluation ===")
try:
    # Récupérer une évaluation de test
    evaluation = Evaluation.objects.first()
    if evaluation:
        print(f"Évaluation de test: {evaluation}")
        
        # Créer une délibération depuis cette évaluation
        deliberation = Deliberation.creer_depuis_evaluation(
            evaluation, 
            'S1', 
            User.objects.first()
        )
        print(f"Délibération créée: {deliberation}")
        print(f"Note finale: {deliberation.calculer_note_finale()}")
        
        # Supprimer la délibération de test
        deliberation.delete()
        print("Délibération de test supprimée")
    else:
        print("Aucune évaluation trouvée pour le test")
        
except Exception as e:
    print(f"Erreur lors du test: {e}")

print("\n=== Test terminé ===")
