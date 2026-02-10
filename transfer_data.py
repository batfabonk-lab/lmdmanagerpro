#!/usr/bin/env python
import os
import sys
import django

# Configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from django.db import connections
from core.models import *
from reglage.models import *

def transfer_data():
    """Transférer les données de SQLite vers MySQL"""
    
    # Obtenir les connexions
    sqlite_conn = connections['default']
    
    # Liste des modèles à transférer
    models_to_transfer = [
        # Models reglage
        ('reglage', 'AnneeAcademique'),
        ('reglage', 'Departement'),
        ('reglage', 'Fonction'),
        ('reglage', 'Grade'),
        ('reglage', 'TypeCharge'),
        ('reglage', 'Mention'),
        ('reglage', 'Niveau'),
        ('reglage', 'Classe'),
        ('reglage', 'Categorie'),
        
        # Models core
        ('core', 'Enseignant'),
        ('core', 'Etudiant'),
        ('core', 'UE'),
        ('core', 'EC'),
        ('core', 'Inscription'),
        ('core', 'Evaluation'),
        ('core', 'Jury'),
        ('core', 'BulletinNotes'),
        ('core', 'CommuniqueDeliberation'),
        ('core', 'CommentaireCours'),
        ('core', 'Recours'),
        ('core', 'Notification'),
        ('core', 'PresenceDeliberation'),
        ('core', 'Deliberation'),
        ('core', 'ParametreEvaluation'),
        ('core', 'CoursAttribution'),
    ]
    
    print("Début du transfert de données...")
    
    for app_label, model_name in models_to_transfer:
        try:
            # Importer le modèle dynamiquement
            model_class = django.apps.apps.get_model(app_label, model_name)
            
            # Compter les enregistrements
            count = model_class.objects.count()
            print(f"{model_name}: {count} enregistrements")
            
            if count > 0:
                print(f"  Transfert de {count} enregistrements...")
                
        except Exception as e:
            print(f"Erreur avec {model_name}: {e}")
    
    print("Transfert terminé!")

if __name__ == '__main__':
    transfer_data()
