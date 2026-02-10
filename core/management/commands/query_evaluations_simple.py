from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Requête SQL simple avec jointures complètes'

    def add_arguments(self, parser):
        parser.add_argument('matricule', type=str, help='Matricule de l\'étudiant')

    def handle(self, *args, **options):
        matricule = options['matricule']
        
        # Requête SQL simplifiée et corrigée
        query = """
        SELECT
            et.matricule_et,
            et.nom_complet,
            et.sexe,
            et.nationalite,
            COALESCE(ue.code_ue, 'N/A') AS code_ue,
            COALESCE(ue.intitule_ue, 'UE sans nom') AS intitule_ue,
            COALESCE(ue.categorie, 'N/A') AS categorie,
            COALESCE(ue.semestre, 0) AS semestre_ue,
            COALESCE(ec.code_ec, 'N/A') AS code_ec,
            COALESCE(ec.intitule_ue, 'EC sans nom') AS intitule_ec,
            COALESCE(ec.credit, ue.credit, 0) AS credits,
            ev.cc,
            ev.examen,
            (ev.cc + ev.examen) AS note,
            CASE
                WHEN (ev.cc + ev.examen) >= 10 THEN 'Validé'
                WHEN (ev.cc + ev.examen) >= 8 THEN 'Compensable'
                ELSE 'Non validé'
            END AS statut,
            ROUND((ev.cc + ev.examen) * COALESCE(ec.credit, ue.credit, 0), 1) AS note_ponderee
        FROM
            core_evaluation ev
        INNER JOIN
            core_etudiant et ON ev.matricule_etudiant_id = et.matricule_et
        LEFT JOIN
            core_ec ec ON ev.code_ec_id = ec.code_ec
        LEFT JOIN
            core_ue ue ON ev.code_ue_id = ue.code_ue
        LEFT JOIN
            core_ue ue_from_ec ON ec.code_ue_id = ue_from_ec.code_ue
        WHERE
            ev.matricule_etudiant_id = %s
            AND ev.cc IS NOT NULL
            AND ev.examen IS NOT NULL
        ORDER BY
            COALESCE(ue_from_ec.semestre, ue.semestre, 0),
            COALESCE(ue_from_ec.code_ue, ue.code_ue, 'ZZ'),
            ec.code_ec;
        """
        
        self.stdout.write("=" * 150)
        self.stdout.write(f"ÉVALUATIONS COMPLÈTES - {matricule}")
        self.stdout.write("=" * 150)
        
        with connection.cursor() as cursor:
            cursor.execute(query, [matricule])
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            
            # Afficher l'en-tête
            header = " | ".join(f"{col:12}" for col in columns)
            self.stdout.write(header)
            self.stdout.write("-" * 150)
            
            # Afficher les résultats
            total_credits = 0
            credits_valides = 0
            total_note_ponderee = 0
            total_credits_pondere = 0
            
            for row in results:
                # Formater chaque colonne
                formatted_row = []
                for i, val in enumerate(row):
                    if val is None:
                        formatted_row.append(f"{'N/A':12}")
                    elif isinstance(val, float):
                        formatted_row.append(f"{val:12.1f}")
                    elif isinstance(val, int):
                        formatted_row.append(f"{val:12}")
                    else:
                        formatted_row.append(f"{str(val)[:12]:12}")
                
                self.stdout.write(" | ".join(formatted_row))
                
                # Calculer les totaux (indices corrects)
                try:
                    credits = int(row[10]) if row[10] and str(row[10]) != 'N/A' and str(row[10]) != 'EC sans nom' else 0
                    total_credits += credits
                    
                    if 'Validé' in str(row[13]):
                        credits_valides += credits
                    
                    note_ponderee = float(row[15]) if row[15] and str(row[15]) != 'N/A' else 0
                    total_note_ponderee += note_ponderee
                    total_credits_pondere += credits
                except (ValueError, IndexError):
                    pass
            
            self.stdout.write("-" * 150)
            self.stdout.write(f"\nNombre total d'évaluations : {len(results)}")
            
            # Afficher les totaux
            self.stdout.write(f"\nCrédits totaux : {total_credits}")
            self.stdout.write(f"Crédits capitalisés : {credits_valides}")
            if total_credits > 0:
                pourcentage = (credits_valides / total_credits) * 100
                self.stdout.write(f"Pourcentage : {pourcentage:.1f}%")
            
            # Moyenne pondérée
            if total_credits_pondere > 0:
                moyenne_ponderee = total_note_ponderee / total_credits_pondere
                self.stdout.write(f"Moyenne pondérée : {moyenne_ponderee:.2f}")
        
        # Requête pour les totaux par catégorie
        query_categories = """
        SELECT
            COALESCE(ue.categorie, ue_from_ec.categorie, 'N/A') AS categorie,
            SUM(COALESCE(ec.credit, ue.credit, 0)) AS credits_total,
            SUM(CASE 
                WHEN (ev.cc + ev.examen) >= 10 THEN COALESCE(ec.credit, ue.credit, 0)
                ELSE 0
            END) AS credits_valides,
            AVG(ev.cc + ev.examen) AS moyenne,
            COUNT(*) AS nombre_evaluations
        FROM
            core_evaluation ev
        INNER JOIN
            core_etudiant et ON ev.matricule_etudiant_id = et.matricule_et
        LEFT JOIN
            core_ec ec ON ev.code_ec_id = ec.code_ec
        LEFT JOIN
            core_ue ue ON ev.code_ue_id = ue.code_ue
        LEFT JOIN
            core_ue ue_from_ec ON ec.code_ue_id = ue_from_ec.code_ue
        WHERE
            ev.matricule_etudiant_id = %s
            AND ev.cc IS NOT NULL
            AND ev.examen IS NOT NULL
        GROUP BY
            COALESCE(ue.categorie, ue_from_ec.categorie, 'N/A')
        ORDER BY
            categorie;
        """
        
        self.stdout.write("\n" + "=" * 150)
        self.stdout.write("RÉCAPITULATIF PAR CATÉGORIE")
        self.stdout.write("=" * 150)
        
        with connection.cursor() as cursor:
            cursor.execute(query_categories, [matricule])
            results = cursor.fetchall()
            
            if results:
                self.stdout.write("Catégorie | Crédits Total | Crédits Validés | Pourcentage | Moyenne | Nb Évaluations")
                self.stdout.write("-" * 120)
                for row in results:
                    categorie, total, valides, moyenne, nb_eval = row
                    pourcentage = (valides / total * 100) if total > 0 else 0
                    self.stdout.write(f"{categorie:9} | {total:12} | {valides:14} | {pourcentage:9.1f}% | {moyenne:7.2f} | {nb_eval:14}")
        
        # Requête pour les totaux par semestre
        query_semestres = """
        SELECT
            COALESCE(ue_from_ec.semestre, ue.semestre, 0) AS semestre,
            SUM(COALESCE(ec.credit, ue.credit, 0)) AS credits_total,
            SUM(CASE 
                WHEN (ev.cc + ev.examen) >= 10 THEN COALESCE(ec.credit, ue.credit, 0)
                ELSE 0
            END) AS credits_valides,
            AVG(ev.cc + ev.examen) AS moyenne,
            COUNT(*) AS nombre_evaluations
        FROM
            core_evaluation ev
        INNER JOIN
            core_etudiant et ON ev.matricule_etudiant_id = et.matricule_et
        LEFT JOIN
            core_ec ec ON ev.code_ec_id = ec.code_ec
        LEFT JOIN
            core_ue ue ON ev.code_ue_id = ue.code_ue
        LEFT JOIN
            core_ue ue_from_ec ON ec.code_ue_id = ue_from_ec.code_ue
        WHERE
            ev.matricule_etudiant_id = %s
            AND ev.cc IS NOT NULL
            AND ev.examen IS NOT NULL
        GROUP BY
            COALESCE(ue_from_ec.semestre, ue.semestre, 0)
        ORDER BY
            semestre;
        """
        
        self.stdout.write("\n" + "=" * 150)
        self.stdout.write("RÉCAPITULATIF PAR SEMESTRE")
        self.stdout.write("=" * 150)
        
        with connection.cursor() as cursor:
            cursor.execute(query_semestres, [matricule])
            results = cursor.fetchall()
            
            if results:
                self.stdout.write("Semestre | Crédits Total | Crédits Validés | Pourcentage | Moyenne | Nb Évaluations")
                self.stdout.write("-" * 120)
                for row in results:
                    semestre, total, valides, moyenne, nb_eval = row
                    pourcentage = (valides / total * 100) if total > 0 else 0
                    self.stdout.write(f"{semestre:8} | {total:12} | {valides:14} | {pourcentage:9.1f}% | {moyenne:7.2f} | {nb_eval:14}")
