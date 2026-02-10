from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Exécute une requête SQL complète avec jointures pour afficher les évaluations détaillées'

    def add_arguments(self, parser):
        parser.add_argument('matricule', type=str, help='Matricule de l\'étudiant')

    def handle(self, *args, **options):
        matricule = options['matricule']
        
        # Requête SQL complète avec jointures
        query = """
        SELECT
            COALESCE(ue.code_ue, 'N/A') AS "Code UE",
            COALESCE(ue.intitule_ue, 'UE sans nom') AS "Intitulé UE",
            COALESCE(ec.code_ec, 'N/A') AS "Code EC",
            COALESCE(ec.intitule_ue, 'EC sans nom') AS "Intitulé EC",
            COALESCE(ue.categorie, 'N/A') AS "Catégorie",
            COALESCE(CASE 
                WHEN ec.credit IS NOT NULL THEN ec.credit
                WHEN ue.credit IS NOT NULL THEN ue.credit
                ELSE 0
            END, 0) AS "Crédits",
            ev.cc AS "CC",
            ev.examen AS "Exam",
            (ev.cc + ev.examen) AS "Note",
            CASE
                WHEN (ev.cc + ev.examen) >= 10 THEN 'Validé'
                WHEN (ev.cc + ev.examen) >= 8 THEN 'Compensable'
                ELSE 'Non validé'
            END AS "Statut",
            COALESCE(ue.semestre, 0) AS "Semestre"
        FROM
            core_evaluation ev
        LEFT JOIN
            core_ec ec ON ev.code_ec_id = ec.code_ec
        LEFT JOIN
            core_ue ue ON ev.code_ue_id = ue.code_ue
        LEFT JOIN
            core_ue ue_ec ON ec.code_ue_id = ue_ec.code_ue
        WHERE
            ev.matricule_etudiant_id = %s
            AND ev.cc IS NOT NULL
            AND ev.examen IS NOT NULL
        ORDER BY
            COALESCE(ue_ec.semestre, ue.semestre, 0),
            COALESCE(ue_ec.code_ue, ue.code_ue, 'ZZ'),
            ec.code_ec;
        """
        
        self.stdout.write("=" * 150)
        self.stdout.write(f"ÉVALUATIONS COMPLÈTES DE {matricule}")
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
            
            for row in results:
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
                
                # Calculer les crédits
                credits = int(row[5]) if row[5] and row[5] != 'N/A' else 0
                total_credits += credits
                if 'Validé' in row[9]:
                    credits_valides += credits
            
            self.stdout.write("-" * 150)
            self.stdout.write(f"\nNombre total d'évaluations : {len(results)}")
            
        # Requête pour les totaux par catégorie
        query_categories = """
        SELECT
            COALESCE(ue.categorie, 'N/A') AS categorie,
            SUM(CASE 
                WHEN ec.credit IS NOT NULL THEN ec.credit
                WHEN ue.credit IS NOT NULL THEN ue.credit
                ELSE 0
            END) AS credits_total,
            SUM(CASE 
                WHEN (ev.cc + ev.examen) >= 10 THEN 
                    CASE 
                        WHEN ec.credit IS NOT NULL THEN ec.credit
                        WHEN ue.credit IS NOT NULL THEN ue.credit
                        ELSE 0
                    END
                ELSE 0
            END) AS credits_valides
        FROM
            core_evaluation ev
        LEFT JOIN
            core_ec ec ON ev.code_ec_id = ec.code_ec
        LEFT JOIN
            core_ue ue ON ev.code_ue_id = ue.code_ue
        LEFT JOIN
            core_ue ue_ec ON ec.code_ue_id = ue_ec.code_ue
        WHERE
            ev.matricule_etudiant_id = %s
            AND ev.cc IS NOT NULL
            AND ev.examen IS NOT NULL
        GROUP BY
            ue.categorie
        ORDER BY
            ue.categorie;
        """
        
        self.stdout.write("\n" + "=" * 150)
        self.stdout.write("RÉCAPITULATIF PAR CATÉGORIE")
        self.stdout.write("=" * 150)
        
        with connection.cursor() as cursor:
            cursor.execute(query_categories, [matricule])
            results = cursor.fetchall()
            
            if results:
                self.stdout.write("Catégorie | Crédits Total | Crédits Validés | Pourcentage")
                self.stdout.write("-" * 50)
                for row in results:
                    categorie, total, valides = row
                    pourcentage = (valides / total * 100) if total > 0 else 0
                    self.stdout.write(f"{categorie:9} | {total:12} | {valides:14} | {pourcentage:9.1f}%")
        
        # Totaux globaux
        self.stdout.write("-" * 50)
        pourcentage_global = (credits_valides / total_credits * 100) if total_credits > 0 else 0
        self.stdout.write(f"{'TOTAL':9} | {total_credits:12} | {credits_valides:14} | {pourcentage_global:9.1f}%")
        
        # Requête pour les moyennes par catégorie
        query_moyennes = """
        SELECT
            COALESCE(ue.categorie, 'N/A') AS categorie,
            AVG(ev.cc + ev.examen) AS moyenne
        FROM
            core_evaluation ev
        LEFT JOIN
            core_ec ec ON ev.code_ec_id = ec.code_ec
        LEFT JOIN
            core_ue ue ON ev.code_ue_id = ue.code_ue
        LEFT JOIN
            core_ue ue_ec ON ec.code_ue_id = ue_ec.code_ue
        WHERE
            ev.matricule_etudiant_id = %s
            AND ev.cc IS NOT NULL
            AND ev.examen IS NOT NULL
        GROUP BY
            ue.categorie
        ORDER BY
            ue.categorie;
        """
        
        self.stdout.write("\n" + "=" * 150)
        self.stdout.write("MOYENNES PAR CATÉGORIE")
        self.stdout.write("=" * 150)
        
        with connection.cursor() as cursor:
            cursor.execute(query_moyennes, [matricule])
            results = cursor.fetchall()
            
            if results:
                self.stdout.write("Catégorie | Moyenne")
                self.stdout.write("-" * 30)
                for row in results:
                    categorie, moyenne = row
                    self.stdout.write(f"{categorie:9} | {moyenne:7.2f}")
                
                # Moyenne globale
                cursor.execute("""
                    SELECT AVG(ev.cc + ev.examen)
                    FROM core_evaluation ev
                    WHERE ev.matricule_etudiant_id = %s
                    AND ev.cc IS NOT NULL
                    AND ev.examen IS NOT NULL
                """, [matricule])
                result = cursor.fetchone()
                if result:
                    moyenne_globale = result[0]
                    self.stdout.write("-" * 30)
                    self.stdout.write(f"{'TOTAL':9} | {moyenne_globale:7.2f}")
