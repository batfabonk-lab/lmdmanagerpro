#!/usr/bin/env python3
"""
Analyse et calcul des crédits pour la nouvelle image
"""

# Liste des cours extraits de la nouvelle image
cours_nouvelle_image = [
    {"code": "TCG122", "intitule": "ANGLAIS", "credit": 5, "note": 11.7, "statut": "Validé"},
    {"code": "TCI111", "intitule": "PROJET 1 (Inclut visites d'usines)", "credit": 5, "note": 14.5, "statut": "Validé"},
    {"code": "TCI112", "intitule": "PROJET 2 (Inclut visites d'usines)", "credit": 5, "note": 5.4, "statut": "Non validé"},
    {"code": "TCI121a", "intitule": "MATHEMATIQUES 1 - Analyse", "credit": 2, "note": 15.5, "statut": "Validé"},
    {"code": "TCI121b", "intitule": "MATHEMATIQUES 1 - Algèbre", "credit": 3, "note": 12.8, "statut": "Validé"},
    {"code": "TCI122a", "intitule": "MATHEMATIQUES 2 - Analyse numerique", "credit": 2, "note": 4.2, "statut": "Non validé"},
    {"code": "TCI122b", "intitule": "MATHEMATIQUES 2 - Probabilite et statistique", "credit": 2, "note": 8.3, "statut": "Non validé"},
    {"code": "TCI122c", "intitule": "MATHEMATIQUES 2 - Recherche operationnelle", "credit": 1, "note": 7.8, "statut": "Non validé"},
    {"code": "TCI123a", "intitule": "PHYSIQUE 1 - Mecanique classique", "credit": 2, "note": 5.9, "statut": "Non validé"},
    {"code": "TCI123b", "intitule": "PHYSIQUE 1 - Electricite", "credit": 1, "note": 8.8, "statut": "Non validé"},
    {"code": "TCI123c", "intitule": "PHYSIQUE 1 - Electronique Generale", "credit": 2, "note": 3.0, "statut": "Non validé"},
    {"code": "TCI123d", "intitule": "PHYSIQUE 1 - Notion de base sur les reseaux", "credit": 3, "note": 11.6, "statut": "Validé"},
    {"code": "TCI124a", "intitule": "PHYSIQUE 2 - Thermodynamique", "credit": 2, "note": 14.5, "statut": "Validé"},
    {"code": "TCI124b", "intitule": "PHYSIQUE 2 - Optique", "credit": 3, "note": 11.3, "statut": "Validé"},
    {"code": "TCI125", "intitule": "CHIMIE - Bases de la chimie", "credit": 2, "note": 13.7, "statut": "Validé"},
    {"code": "TCI126", "intitule": "CHIMIE 2:Materiaux", "credit": 5, "note": 8.0, "statut": "Non validé"},
    {"code": "TCI127_a", "intitule": "INFORMATIQUE 1 - Base de l'architecture des syst. Informatique", "credit": 2, "note": 12.9, "statut": "Validé"},
    {"code": "TCI127_b", "intitule": "INFORMATIQUE 1 - Bases du developpement de logiciel", "credit": 3, "note": 8.2, "statut": "Validé"},
    # La liste semble coupée, il y a probablement d'autres cours après TCI128a
]

def analyser_cours():
    """Analyse détaillée des cours de la nouvelle image"""
    credits_total = 0
    credits_capitalises = 0
    
    print("ANALYSE DÉTAILLÉE DES COURS - NOUVELLE IMAGE")
    print("=" * 120)
    print(f"{'N°':<3} {'Code':<9} {'Intitulé':<50} {'Crédit':<8} {'Note':<7} {'Validé':<8} {'Capitalisé':<10}")
    print("-" * 120)
    
    valides = []
    non_valides = []
    
    for i, cours in enumerate(cours_nouvelle_image, 1):
        credit = cours['credit']
        note = cours['note']
        intitule = cours['intitule'][:48] + "..." if len(cours['intitule']) > 48 else cours['intitule']
        
        # Règle: note >= 10 = validé
        valide = note >= 10
        credit_capitalise = credit if valide else 0
        
        credits_total += credit
        credits_capitalises += credit_capitalise
        
        valide_str = "OUI" if valide else "NON"
        capitalise_str = f"+{credit_capitalise}" if credit_capitalise > 0 else "0"
        
        print(f"{i:<3} {cours['code']:<9} {intitule:<50} {credit:<8} {note:<7.1f} {valide_str:<8} {capitalise_str:<10}")
        
        if valide:
            valides.append(cours)
        else:
            non_valides.append(cours)
    
    print("-" * 120)
    print(f"RÉSULTAT FINAL:")
    print(f"  Total cours: {len(cours_nouvelle_image)}")
    print(f"  Total crédits: {credits_total}")
    print(f"  Crédits capitalisés: {credits_capitalises}")
    print(f"  Pourcentage: {credits_capitalises/credits_total*100:.1f}%")
    print(f"  Cours validés: {len(valides)}")
    print(f"  Cours non validés: {len(non_valides)}")
    
    print("\n" + "=" * 120)
    print("DÉTAIL DES COURS VALIDÉS:")
    for c in valides:
        print(f"  {c['code']} - {c['intitule']} - {c['note']}/10 - {c['credit']} crédits")
    
    print("\nDÉTAIL DES COURS NON VALIDÉS:")
    for c in non_valides:
        print(f"  {c['code']} - {c['intitule']} - {c['note']}/10 - {c['credit']} crédits")
    
    print("\n" + "=" * 120)
    print("NOTE: La liste semble incomplète (coupée à TCI127_b)")
    print("Il y a probablement d'autres cours non visibles dans cette image.")

if __name__ == "__main__":
    analyser_cours()
