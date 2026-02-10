#!/usr/bin/env python
import os
import sys
import django
import sqlite3
import json

# Configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from django.db import connections, transaction
from core.models import *
from reglage.models import *

def export_sqlite_data():
    """Exporter les données de SQLite vers des fichiers JSON"""
    
    # Connexion à la base SQLite
    sqlite_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    # Lister toutes les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Exportation des données SQLite...")
    
    for table_name, in tables:
        if table_name not in ['django_migrations', 'django_content_type', 'auth_permission', 'auth_group', 'auth_group_permissions', 'auth_user_groups', 'auth_user_user_permissions', 'django_session', 'django_admin_log']:
            try:
                cursor.execute(f"SELECT * FROM {table_name}")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                # Convertir en liste de dictionnaires
                data = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    data.append(row_dict)
                
                # Sauvegarder en JSON
                filename = f"{table_name}_data.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                
                print(f"  {table_name}: {len(data)} enregistrements exportés")
                
            except Exception as e:
                print(f"  Erreur avec {table_name}: {e}")
    
    conn.close()
    print("Exportation terminée!")

def import_mysql_data():
    """Importer les données JSON dans MySQL"""
    
    # Liste des modèles et leurs fichiers JSON correspondants
    model_files = [
        ('reglage.AnneeAcademique', 'reglage_anneeacademique_data.json'),
        ('reglage.Departement', 'reglage_departement_data.json'),
        ('reglage.Fonction', 'reglage_fonction_data.json'),
        ('reglage.Grade', 'reglage_grade_data.json'),
        ('reglage.TypeCharge', 'reglage_typecharge_data.json'),
        ('reglage.Mention', 'reglage_mention_data.json'),
        ('reglage.Niveau', 'reglage_niveau_data.json'),
        ('reglage.Classe', 'reglage_classe_data.json'),
        ('reglage.Categorie', 'reglage_categorie_data.json'),
        ('core.Enseignant', 'core_enseignant_data.json'),
        ('core.Etudiant', 'core_etudiant_data.json'),
        ('core.UE', 'core_ue_data.json'),
        ('core.EC', 'core_ec_data.json'),
        ('core.Inscription', 'core_inscription_data.json'),
        ('core.Evaluation', 'core_evaluation_data.json'),
        ('core.Jury', 'core_jury_data.json'),
        ('core.BulletinNotes', 'core_bulletinnotes_data.json'),
        ('core.CommuniqueDeliberation', 'core_communedeliberation_data.json'),
        ('core.CommentaireCours', 'core_commentairecours_data.json'),
        ('core.Recours', 'core_recours_data.json'),
        ('core.Notification', 'core_notification_data.json'),
        ('core.PresenceDeliberation', 'core_presencedeliberation_data.json'),
        ('core.Deliberation', 'core_deliberation_data.json'),
        ('core.ParametreEvaluation', 'core_parametreevaluation_data.json'),
        ('core.CoursAttribution', 'core_coursattribution_data.json'),
    ]
    
    print("Importation des données dans MySQL...")
    
    with transaction.atomic():
        for model_path, json_file in model_files:
            if os.path.exists(json_file):
                try:
                    # Charger les données JSON
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if not data:
                        print(f"  {model_path}: pas de données")
                        continue
                    
                    # Obtenir le modèle
                    model_class = django.apps.apps.get_model(model_path)
                    
                    # Importer les données
                    count = 0
                    for item in data:
                        try:
                            # Nettoyer les données (supprimer les champs non existants)
                            model_fields = [f.name for f in model_class._meta.fields]
                            clean_data = {k: v for k, v in item.items() if k in model_fields}
                            
                            # Créer l'objet
                            obj = model_class(**clean_data)
                            obj.save()
                            count += 1
                        except Exception as e:
                            print(f"    Erreur lors de l'importation d'un enregistrement: {e}")
                    
                    print(f"  {model_path}: {count} enregistrements importés")
                    
                except Exception as e:
                    print(f"  Erreur avec {model_path}: {e}")
            else:
                print(f"  Fichier {json_file} non trouvé")
    
    print("Importation terminée!")

def main():
    """Fonction principale"""
    print("Migration SQLite vers MySQL")
    print("=" * 40)
    
    # Étape 1: Exporter depuis SQLite
    export_sqlite_data()
    
    print("\n" + "=" * 40)
    
    # Étape 2: Importer vers MySQL
    import_mysql_data()
    
    print("\nMigration terminée!")

if __name__ == '__main__':
    main()
