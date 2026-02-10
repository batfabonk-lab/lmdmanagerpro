import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("=== COURS DANS ATTRIBUTION POUR L1INFO ===\n")

# Requête pour récupérer les cours attribués à L1INFO
query = """
SELECT 
    ca.code_cours,
    ca.intitule,
    ca.credit,
    ca.type_cours,
    ca.semestre
FROM cours_attribution ca
WHERE ca.classe_id = 'L1INFO'
ORDER BY ca.semestre, ca.code_cours
"""

cursor.execute(query)
results = cursor.fetchall()

if results:
    print(f"{'Code':<15} | {'Intitulé':<50} | {'Crédits':<8} | {'Type':<5} | {'Semestre'}")
    print("-" * 100)
    
    total_credits = 0
    for row in results:
        code, intitule, credit, type_cours, semestre = row
        print(f"{code:<15} | {intitule:<50} | {credit:<8} | {type_cours:<5} | S{semestre}")
        total_credits += credit
    
    print("-" * 100)
    print(f"\n=== TOTAL: {len(results)} cours | {total_credits} crédits ===\n")
    
    # Vérifier les attributions aux enseignants
    query_attr = """
    SELECT 
        a.code_cours,
        e.nom_complet,
        a.annee_academique
    FROM core_attribution a
    JOIN core_enseignant e ON a.matricule_en_id = e.matricule_en
    WHERE a.code_cours IN (
        SELECT code_cours FROM cours_attribution WHERE classe_id = 'L1INFO'
    )
    ORDER BY a.code_cours
    """
    
    cursor.execute(query_attr)
    attributions = cursor.fetchall()
    
    if attributions:
        print("\n=== ENSEIGNANTS ATTRIBUÉS ===\n")
        print(f"{'Code Cours':<15} | {'Enseignant':<40} | {'Année Académique'}")
        print("-" * 80)
        for attr in attributions:
            code_cours, nom_enseignant, annee = attr
            print(f"{code_cours:<15} | {nom_enseignant:<40} | {annee}")
else:
    print("Aucun cours trouvé pour L1INFO")

conn.close()
