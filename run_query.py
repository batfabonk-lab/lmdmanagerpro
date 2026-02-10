import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanager.settings')
django.setup()

from django.db import connection

# Requête SQL
query = """
SELECT
    code_ue_id AS "Code UE",
    code_ec_id AS "Code EC",
    cc AS "CC",
    examen AS "Exam",
    (cc + examen) AS "Note",
    CASE
        WHEN (cc + examen) >= 10 THEN 'Validé'
        ELSE 'Non validé'
    END AS "Statut"
FROM
    core_evaluation
WHERE
    matricule_etudiant_id = 'ETU001'
    AND cc IS NOT NULL
    AND examen IS NOT NULL
ORDER BY
    code_ue_id, code_ec_id;
"""

print("=" * 100)
print("RÉSULTATS DE LA REQUÊTE - Évaluations de ETU001")
print("=" * 100)

with connection.cursor() as cursor:
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    results = cursor.fetchall()
    
    # Afficher l'en-tête
    header = " | ".join(f"{col:15}" for col in columns)
    print(header)
    print("-" * 100)
    
    # Afficher les résultats
    for row in results:
        formatted_row = []
        for val in row:
            if val is None:
                formatted_row.append(f"{'NULL':15}")
            elif isinstance(val, (float, int)):
                formatted_row.append(f"{val:15.1f}" if isinstance(val, float) else f"{val:15}")
            else:
                formatted_row.append(f"{str(val):15}")
        print(" | ".join(formatted_row))
    
    print("-" * 100)
    print(f"\nNombre total d'évaluations : {len(results)}")

# Requête pour calculer les crédits
query_credits = """
SELECT
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
WHERE
    ev.matricule_etudiant_id = 'ETU001'
    AND ev.cc IS NOT NULL
    AND ev.examen IS NOT NULL;
"""

print("\n" + "=" * 100)
print("CALCUL DES CRÉDITS")
print("=" * 100)

with connection.cursor() as cursor:
    cursor.execute(query_credits)
    result = cursor.fetchone()
    if result:
        credits_total, credits_valides = result
        print(f"Crédits totaux      : {credits_total}")
        print(f"Crédits capitalisés : {credits_valides}")
        if credits_total and credits_total > 0:
            pourcentage = (credits_valides / credits_total) * 100
            print(f"Pourcentage         : {pourcentage:.1f}%")
