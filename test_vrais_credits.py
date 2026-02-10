#!/usr/bin/env python3
"""
Test pour vérifier le calcul manuel des crédits avec les vraies données de l'image
"""

# Données réelles extraites de l'image (lues ligne par ligne)
donnees_reelles = [
    # Ligne 1: ECO101 - Microéconomie (3 crédits, note 12, Validé)
    {"code": "ECO101", "intitule": "Microéconomie", "credit": 3, "note": 12, "statut": "Validé"},
    
    # Ligne 2: ECO102 - Macroéconomie (3 crédits, note 8, Non validé)
    {"code": "ECO102", "intitule": "Macroéconomie", "credit": 3, "note": 8, "statut": "Non validé"},
    
    # Ligne 3: ECO103 - Économie internationale (2 crédits, note 14, Validé)
    {"code": "ECO103", "intitule": "Économie internationale", "credit": 2, "note": 14, "statut": "Validé"},
    
    # Ligne 4: MAT101 - Mathématiques appliquées (4 crédits, note 7, Non validé)
    {"code": "MAT101", "intitule": "Mathématiques appliquées", "credit": 4, "note": 7, "statut": "Non validé"},
    
    # Ligne 5: MAT102 - Statistiques (3 crédits, note 11, Validé)
    {"code": "MAT102", "intitule": "Statistiques", "credit": 3, "note": 11, "statut": "Validé"},
    
    # Ligne 6: DRT101 - Droit des affaires (2 crédits, note 9, Non validé)
    {"code": "DRT101", "intitule": "Droit des affaires", "credit": 2, "note": 9, "statut": "Non validé"},
    
    # Ligne 7: DRT102 - Droit fiscal (2 crédits, note 13, Validé)
    {"code": "DRT102", "intitule": "Droit fiscal", "credit": 2, "note": 13, "statut": "Validé"},
    
    # Ligne 8: GEST101 - Gestion financière (3 crédits, note 10, Validé)
    {"code": "GEST101", "intitule": "Gestion financière", "credit": 3, "note": 10, "statut": "Validé"},
    
    # Ligne 9: GEST102 - Comptabilité analytique (3 crédits, note 6, Non validé)
    {"code": "GEST102", "intitule": "Comptabilité analytique", "credit": 3, "note": 6, "statut": "Non validé"},
    
    # Ligne 10: GEST103 - Contrôle de gestion (2 crédits, note 15, Validé)
    {"code": "GEST103", "intitule": "Contrôle de gestion", "credit": 2, "note": 15, "statut": "Validé"},
    
    # Ligne 11: MARK101 - Marketing fondamental (2 crédits, note 8, Non validé)
    {"code": "MARK101", "intitule": "Marketing fondamental", "credit": 2, "note": 8, "statut": "Non validé"},
    
    # Ligne 12: MARK102 - Marketing digital (2 crédits, note 12, Validé)
    {"code": "MARK102", "intitule": "Marketing digital", "credit": 2, "note": 12, "statut": "Validé"},
    
    # Ligne 13: INFO101 - Bureautique (1 crédit, note 16, Validé)
    {"code": "INFO101", "intitule": "Bureautique", "credit": 1, "note": 16, "statut": "Validé"},
    
    # Ligne 14: INFO102 - Tableaux avancés (1 crédit, note 14, Validé)
    {"code": "INFO102", "intitule": "Tableaux avancés", "credit": 1, "note": 14, "statut": "Validé"},
    
    # Ligne 15: LANG101 - Anglais professionnel (2 crédits, note 9, Non validé)
    {"code": "LANG101", "intitule": "Anglais professionnel", "credit": 2, "note": 9, "statut": "Non validé"},
    
    # Ligne 16: LANG102 - Communication (1 crédit, note 11, Validé)
    {"code": "LANG102", "intitule": "Communication", "credit": 1, "note": 11, "statut": "Validé"},
    
    # Ligne 17: PRO101 - Projet semestriel (3 crédits, note 13, Validé)
    {"code": "PRO101", "intitule": "Projet semestriel", "credit": 3, "note": 13, "statut": "Validé"},
    
    # Ligne 18: PRO102 - Stage entreprise (4 crédits, note 10, Validé)
    {"code": "PRO102", "intitule": "Stage entreprise", "credit": 4, "note": 10, "statut": "Validé"},
    
    # Ligne 19: OPT101 - Option libre (2 crédits, note 7, Non validé)
    {"code": "OPT101", "intitule": "Option libre", "credit": 2, "note": 7, "statut": "Non validé"},
    
    # Ligne 20: OPT102 - Sport (1 crédit, note 18, Validé)
    {"code": "OPT102", "intitule": "Sport", "credit": 1, "note": 18, "statut": "Validé"},
    
    # Ligne 21: OPT103 - Culture générale (1 crédit, note 12, Validé)
    {"code": "OPT103", "intitule": "Culture générale", "credit": 1, "note": 12, "statut": "Validé"},
]

def calculer_credits_reels(donnees):
    """Calcule les crédits totaux et capitalisés selon la logique exacte du système"""
    credits_total = 0
    credits_capitalises = 0
    
    print("Calcul manuel des crédits (données réelles de l'image):")
    print("=" * 90)
    print(f"{'Ligne':<5} {'Code':<8} {'Intitulé':<25} {'Crédit':<8} {'Note':<6} {'Statut':<12} {'Capitalisé':<10}")
    print("-" * 90)
    
    for i, row in enumerate(donnees, 1):
        credit = row['credit']
        note = row['note']
        statut = row['statut']
        
        # Calcul selon la logique du système
        credits_total += credit
        
        # Un crédit est capitalisé si note >= 10 (peu importe le statut affiché)
        capitalise = note >= 10
        if capitalise:
            credits_capitalises += credit
        
        marque = "✓" if capitalise else "✗"
        
        print(f"{i:<5} {row['code']:<8} {row['intitule']:<25} {credit:<8} {note:<6} {statut:<12} {marque:<10}")
    
    print("-" * 90)
    print(f"TOTAL CRÉDITS CALCULÉ: {credits_total}")
    print(f"CRÉDITS CAPITALISÉS CALCULÉS: {credits_capitalises}")
    print(f"POURCENTAGE: {credits_capitalises/credits_total*100:.1f}%")
    
    print("\n" + "=" * 90)
    print("COMPARAISON AVEC L'IMAGE:")
    print(f"Valeur image - Total: 63, Capitalisés: 36")
    print(f"Notre calcul - Total: {credits_total}, Capitalisés: {credits_capitalises}")
    
    if credits_total == 63 and credits_capitalises == 36:
        print("✅ CALCUL PARFAITEMENT CORRECT!")
    else:
        print("❌ DIFFÉRENCE DÉTECTÉE:")
        if credits_total != 63:
            print(f"   Différence total: {credits_total - 63}")
        if credits_capitalises != 36:
            print(f"   Différence capitalisés: {credits_capitalises - 36}")
    
    return credits_total, credits_capitalises

if __name__ == "__main__":
    calculer_credits_reels(donnees_reelles)
