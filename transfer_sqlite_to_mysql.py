#!/usr/bin/env python
import os
import sys
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from django.db import transaction
from reglage.models import (
    Section as ReglageSection, Departement as ReglageDepartement,
    Mention, Niveau, Semestre, Classe, AnneeAcademique,
    Grade, Fonction, TypeCharge, Categorie
)
from core.models import (
    Section, Departement, UE, EC, Enseignant, Etudiant,
    Inscription, Evaluation, Jury, BulletinNotes, CoursAttribution
)

def transfer_from_sqlite():
    """Transférer les données de SQLite vers MySQL"""
    
    # Connexion à SQLite
    sqlite_db = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    if not os.path.exists(sqlite_db):
        print(f"Erreur: Le fichier {sqlite_db} n'existe pas!")
        return False
    
    conn = sqlite3.connect(sqlite_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("Transfert des données de SQLite vers MySQL...")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # 1. Sections
            print("\n1. Transfert des Sections...")
            cursor.execute("SELECT * FROM reglage_section")
            rows = cursor.fetchall()
            for row in rows:
                Section.objects.update_or_create(
                    code_section=row['code_section'],
                    defaults={'designation_sc': row['designation_section']}
                )
            print(f"   ✓ {len(rows)} sections transférées")
            
            # 2. Départements
            print("\n2. Transfert des Départements...")
            cursor.execute("SELECT * FROM reglage_departement")
            rows = cursor.fetchall()
            for row in rows:
                try:
                    section = Section.objects.get(code_section=row['code_section_id'])
                    Departement.objects.update_or_create(
                        code_dpt=row['code_departement'],
                        defaults={
                            'designation_dpt': row['designation_departement'],
                            'code_section': section
                        }
                    )
                except Section.DoesNotExist:
                    print(f"   ! Section {row['code_section_id']} non trouvée pour département {row['code_departement']}")
            print(f"   ✓ {len(rows)} départements transférés")
            
            # 3. Mentions
            print("\n3. Transfert des Mentions...")
            cursor.execute("SELECT * FROM reglage_mention")
            rows = cursor.fetchall()
            for row in rows:
                Mention.objects.update_or_create(
                    code_mention=row['code_mention'],
                    defaults={'designation_mention': row['designation_mention']}
                )
            print(f"   ✓ {len(rows)} mentions transférées")
            
            # 4. Niveaux
            print("\n4. Transfert des Niveaux...")
            cursor.execute("SELECT * FROM reglage_niveau")
            rows = cursor.fetchall()
            for row in rows:
                Niveau.objects.update_or_create(
                    code_niveau=row['code_niveau'],
                    defaults={'designation_niveau': row['designation_niveau']}
                )
            print(f"   ✓ {len(rows)} niveaux transférés")
            
            # 5. Semestres
            print("\n5. Transfert des Semestres...")
            cursor.execute("SELECT * FROM reglage_semestre")
            rows = cursor.fetchall()
            for row in rows:
                Semestre.objects.update_or_create(
                    code_semestre=row['code_semestre'],
                    defaults={'designation_semestre': row['designation_semestre']}
                )
            print(f"   ✓ {len(rows)} semestres transférés")
            
            # 6. Classes
            print("\n6. Transfert des Classes...")
            cursor.execute("SELECT * FROM reglage_classe")
            rows = cursor.fetchall()
            for row in rows:
                try:
                    niveau = Niveau.objects.get(code_niveau=row['code_niveau_id']) if row['code_niveau_id'] else None
                    mention = Mention.objects.get(code_mention=row['code_mention_id']) if row['code_mention_id'] else None
                    # Utiliser save() au lieu de update_or_create car le modèle génère automatiquement code_classe
                    classe, created = Classe.objects.get_or_create(
                        code_niveau=niveau,
                        code_mention=mention,
                        defaults={
                            'code_classe': row['code_classe'],
                            'designation_classe': row['designation_classe']
                        }
                    )
                    if not created:
                        classe.code_classe = row['code_classe']
                        classe.designation_classe = row['designation_classe']
                        classe.save()
                except (Niveau.DoesNotExist, Mention.DoesNotExist) as e:
                    print(f"   ! Erreur pour classe {row['code_classe']}: {e}")
            print(f"   ✓ {len(rows)} classes transférées")
            
            # 7. Années académiques
            print("\n7. Transfert des Années Académiques...")
            cursor.execute("SELECT * FROM reglage_anneeacademique")
            rows = cursor.fetchall()
            for row in rows:
                AnneeAcademique.objects.update_or_create(
                    code_anac=row['code_anac'],
                    defaults={
                        'designation_anac': row['designation_anac'],
                        'date_debut': row['date_debut'],
                        'date_fin': row['date_fin'],
                        'active': bool(row['active'])
                    }
                )
            print(f"   ✓ {len(rows)} années académiques transférées")
            
            # 8. Grades
            print("\n8. Transfert des Grades...")
            cursor.execute("SELECT * FROM reglage_grade")
            rows = cursor.fetchall()
            for row in rows:
                Grade.objects.update_or_create(
                    code_grade=row['code_grade'],
                    defaults={'designation_grade': row['designation_grade']}
                )
            print(f"   ✓ {len(rows)} grades transférés")
            
            # 9. Fonctions
            print("\n9. Transfert des Fonctions...")
            cursor.execute("SELECT * FROM reglage_fonction")
            rows = cursor.fetchall()
            for row in rows:
                Fonction.objects.update_or_create(
                    code_fonction=row['code_fonction'],
                    defaults={'designation_fonction': row['designation_fonction']}
                )
            print(f"   ✓ {len(rows)} fonctions transférées")
            
            # 10. Types de charge
            print("\n10. Transfert des Types de Charge...")
            try:
                cursor.execute("SELECT * FROM reglage_typecharge")
                rows = cursor.fetchall()
                for row in rows:
                    TypeCharge.objects.update_or_create(
                        code_type=row['code_type'],
                        defaults={'designation_typecharge': row['designation_typecharge']}
                    )
                print(f"   ✓ {len(rows)} types de charge transférés")
            except (sqlite3.OperationalError, IndexError) as e:
                print(f"   ! Erreur lors du transfert des types de charge: {e}")
            
            # 11. Catégories
            print("\n11. Transfert des Catégories...")
            cursor.execute("SELECT * FROM reglage_categorie")
            rows = cursor.fetchall()
            for row in rows:
                Categorie.objects.update_or_create(
                    code_categorie=row['code_categorie'],
                    defaults={'designation_categorie': row['designation_categorie']}
                )
            print(f"   ✓ {len(rows)} catégories transférées")
            
            # 12. Enseignants
            print("\n12. Transfert des Enseignants...")
            cursor.execute("SELECT * FROM core_enseignant")
            rows = cursor.fetchall()
            count = 0
            for row in rows:
                try:
                    Enseignant.objects.update_or_create(
                        matricule_en=row['matricule_en'],
                        defaults={
                            'nom_complet': row['nom_complet'],
                            'telephone': row['telephone'] or '',
                            'fonction': row['fonction_id'] or '',
                            'grade': row['grade_id'] or '',
                            'categorie': row['categorie_id'] or '',
                            'code_dpt': row['code_dpt_id'] or '',
                            'code_section': row['code_section_id'] or '',
                            'photo': row['photo'] or ''
                        }
                    )
                    count += 1
                except Exception as e:
                    print(f"   ! Erreur pour enseignant {row['matricule_en']}: {e}")
            print(f"   ✓ {count} enseignants transférés")
            
            # 13. Étudiants
            print("\n13. Transfert des Étudiants...")
            cursor.execute("SELECT * FROM core_etudiant")
            rows = cursor.fetchall()
            count = 0
            for row in rows:
                try:
                    Etudiant.objects.update_or_create(
                        matricule_et=row['matricule_et'],
                        defaults={
                            'nom_complet': row['nom_complet'],
                            'sexe': row['sexe'] or '',
                            'date_naiss': row['date_naiss'],
                            'nationalite': row['nationalite'] or '',
                            'telephone': row['telephone'] or '',
                            'photo': row['photo'] or ''
                        }
                    )
                    count += 1
                except Exception as e:
                    print(f"   ! Erreur pour étudiant {row['matricule_et']}: {e}")
            print(f"   ✓ {count} étudiants transférés")
            
            # 14. UE
            print("\n14. Transfert des UE...")
            cursor.execute("SELECT * FROM core_ue")
            rows = cursor.fetchall()
            for row in rows:
                try:
                    classe = Classe.objects.get(code_classe=row['code_classe_id']) if row['code_classe_id'] else None
                    UE.objects.update_or_create(
                        code_ue=row['code_ue'],
                        defaults={
                            'intitule_ue': row['intitule_ue'],
                            'credit': row['credit'],
                            'semestre': row['semestre'] or 1,
                            'seuil': row['seuil'] or 50,
                            'categorie': row['categorie'] or 'A',
                            'classe': classe
                        }
                    )
                except Exception as e:
                    print(f"   ! Erreur pour UE {row['code_ue']}: {e}")
            print(f"   ✓ {len(rows)} UE transférées")
            
            # 15. EC
            print("\n15. Transfert des EC...")
            cursor.execute("SELECT * FROM core_ec")
            rows = cursor.fetchall()
            for row in rows:
                try:
                    ue = UE.objects.get(code_ue=row['code_ue_id']) if row['code_ue_id'] else None
                    classe = Classe.objects.get(code_classe=row['code_classe_id']) if row['code_classe_id'] else None
                    EC.objects.update_or_create(
                        code_ec=row['code_ec'],
                        defaults={
                            'intitule_ue': row['intitule_ue'],
                            'credit': row['credit'],
                            'seuil': row['seuil'] or 8,
                            'categorie': row['categorie'] or '',
                            'code_ue': ue,
                            'classe': classe
                        }
                    )
                except Exception as e:
                    print(f"   ! Erreur pour EC {row['code_ec']}: {e}")
            print(f"   ✓ {len(rows)} EC transférés")
            
            # 16. Inscriptions
            print("\n16. Transfert des Inscriptions...")
            cursor.execute("SELECT * FROM core_inscription")
            rows = cursor.fetchall()
            for row in rows:
                try:
                    etudiant = Etudiant.objects.get(id_lgn=row['id_lgn_id'])
                    classe = Classe.objects.get(code_classe=row['code_classe_id'])
                    annee = AnneeAcademique.objects.get(code_anac=row['code_anac_id'])
                    Inscription.objects.update_or_create(
                        matricule=row['matricule'],
                        defaults={
                            'id_lgn': etudiant,
                            'code_classe': classe,
                            'code_anac': annee,
                            'cohorte': row.get('cohorte', '')
                        }
                    )
                except Exception as e:
                    print(f"   ! Erreur pour inscription {row['matricule']}: {e}")
            print(f"   ✓ {len(rows)} inscriptions transférées")
            
            # 17. Évaluations
            print("\n17. Transfert des Évaluations...")
            cursor.execute("SELECT * FROM core_evaluation")
            rows = cursor.fetchall()
            count = 0
            for row in rows:
                try:
                    ec = EC.objects.get(code_ec=row['code_ec_id'])
                    inscription = Inscription.objects.get(matricule=row['matricule_id'])
                    Evaluation.objects.update_or_create(
                        code_ec=ec,
                        matricule=inscription,
                        defaults={
                            'cc': row.get('cc'),
                            'examen': row.get('examen'),
                            'rattrapage': row.get('rattrapage'),
                            'rachat': row.get('rachat'),
                            'enseignement': row.get('enseignement')
                        }
                    )
                    count += 1
                except Exception as e:
                    pass
            print(f"   ✓ {count} évaluations transférées")
            
            # 18. Jury
            print("\n18. Transfert des Jury...")
            cursor.execute("SELECT * FROM core_jury")
            rows = cursor.fetchall()
            count = 0
            for row in rows:
                try:
                    inscription = Inscription.objects.get(matricule=row['matricule_id'])
                    Jury.objects.update_or_create(
                        id_lgn=row['id_lgn'],
                        defaults={
                            'matricule': inscription,
                            'decision': row.get('decision', '')
                        }
                    )
                    count += 1
                except Exception as e:
                    pass
            print(f"   ✓ {count} jurys transférés")
            
            print("\n" + "=" * 60)
            print("✓ Transfert terminé avec succès!")
            return True
            
    except Exception as e:
        print(f"\n✗ Erreur lors du transfert: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

def verify_transfer():
    """Vérifier le transfert"""
    print("\nVérification des données transférées:")
    print("=" * 60)
    
    models = [
        ('Sections', Section),
        ('Départements', Departement),
        ('Mentions', Mention),
        ('Niveaux', Niveau),
        ('Semestres', Semestre),
        ('Classes', Classe),
        ('Années Académiques', AnneeAcademique),
        ('Grades', Grade),
        ('Fonctions', Fonction),
        ('Types de Charge', TypeCharge),
        ('Catégories', Categorie),
        ('Enseignants', Enseignant),
        ('Étudiants', Etudiant),
        ('UE', UE),
        ('EC', EC),
        ('Inscriptions', Inscription),
        ('Évaluations', Evaluation),
        ('Jury', Jury),
    ]
    
    for name, model in models:
        count = model.objects.count()
        print(f"  {name}: {count} enregistrements")

if __name__ == '__main__':
    if transfer_from_sqlite():
        verify_transfer()
