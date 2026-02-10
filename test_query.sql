SELECT
    code_ue_id AS "Code",
    cc AS "CC",
    examen AS "Exam",
    (cc + examen) AS "Note",
    (cc + examen) AS "N.Pd",
    CASE
        WHEN (cc + examen) >= 10 THEN 'Validé'
        ELSE 'Non validé'
    END AS "Statut"
FROM
    core_evaluation
WHERE
    matricule_etudiant_id = 'ETU001';
