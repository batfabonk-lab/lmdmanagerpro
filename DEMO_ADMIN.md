# 🎬 Démonstration Admin - Système LMD

## 🚀 Accès Rapide

**URL** : http://localhost:8000/admin/
**Compte** : `admin` / `admin123`

---

## 📺 Démonstration en 5 Minutes

### 1️⃣ Connexion (30 secondes)
```
1. Ouvrez http://localhost:8000/admin/
2. Entrez : admin / admin123
3. Cliquez sur "Se connecter"
```

**Résultat** : Vous voyez le tableau de bord avec toutes les entités

---

### 2️⃣ Gérer les Étudiants (1 minute)

#### Voir la liste
```
1. Cliquez sur "Étudiants"
2. Vous voyez : ET2024001 - Jean Kabongo
```

#### Ajouter un étudiant
```
1. Cliquez sur "Ajouter Étudiant"
2. Remplissez :
   - Matricule : ET2024002
   - Nom : Marie Tshala
   - Sexe : F
   - Date naissance : 2003-03-15
   - Nationalité : Congolaise
   - Téléphone : +243 900 000 003
   - Cohorte : L1-2024
   - Compte : etudiant1 (temporaire)
3. Cliquez sur "Enregistrer"
```

#### Exporter en CSV
```
1. Cochez les étudiants
2. Action → "Exporter les étudiants sélectionnés (CSV)"
3. Cliquez sur "Exécuter"
4. Le fichier etudiants.csv est téléchargé
```

---

### 3️⃣ Gérer les Enseignants (1 minute)

#### Voir la liste
```
1. Cliquez sur "Enseignants"
2. Vous voyez : EN2024001 - Prof. Marie Tshimanga
```

#### Ajouter un enseignant
```
1. Cliquez sur "Ajouter Enseignant"
2. Remplissez :
   - Matricule : EN2024002
   - Nom : Dr. Joseph Mukendi
   - Grade : Chargé de Cours
   - Fonction : Enseignant
   - Département : INFO-L1
   - Téléphone : +243 900 000 004
   - Compte : enseignant1 (temporaire)
3. Cliquez sur "Enregistrer"
```

#### Filtrer par grade
```
1. Dans la barre latérale droite
2. Cliquez sur "Professeur" ou "Chargé de Cours"
3. La liste se filtre automatiquement
```

---

### 4️⃣ Gérer les UE (1 minute)

#### Voir la liste
```
1. Cliquez sur "Unités d'Enseignement"
2. Vous voyez : UE101, UE102
```

#### Ajouter une UE
```
1. Cliquez sur "Ajouter Unité d'Enseignement"
2. Remplissez :
   - Code : UE103
   - Intitulé : Algorithmique et Structures de Données
   - Crédits : 6
   - CMI : 60
   - TP/TD : TP
   - Semestre : 1
3. Cliquez sur "Enregistrer"
```

#### Dupliquer une UE
```
1. Cochez UE103
2. Action → "Dupliquer les UE sélectionnées"
3. Cliquez sur "Exécuter"
4. Une copie UE103_COPIE est créée
```

---

### 5️⃣ Gérer les EC (1 minute)

#### Voir la liste
```
1. Cliquez sur "Éléments Constitutifs"
2. Vous voyez : EC101, EC102
```

#### Ajouter un EC
```
1. Cliquez sur "Ajouter Élément Constitutif"
2. Remplissez :
   - Code : EC103
   - Intitulé : Algorithmes de tri
   - UE : UE103
   - Crédits : 3
   - CMI : 30
   - TP/TD : TP
3. Cliquez sur "Enregistrer"
```

#### Filtrer par UE
```
1. Dans la barre latérale droite
2. Cliquez sur une UE (ex: UE101)
3. Seuls les EC de cette UE s'affichent
```

---

### 6️⃣ Gérer les Jurys (30 secondes)

#### Voir la liste
```
1. Cliquez sur "Jurys"
2. Vous voyez : JURY-L1-2024
```

#### Modifier un jury
```
1. Cliquez sur "JURY-L1-2024"
2. Modifiez la composition si nécessaire
3. Cliquez sur "Enregistrer"
```

#### Exporter les jurys
```
1. Cochez les jurys
2. Action → "Exporter les jurys sélectionnés (CSV)"
3. Cliquez sur "Exécuter"
```

---

## 🎯 Fonctionnalités Testées

### ✅ Étudiants
- [x] Voir la liste
- [x] Ajouter un étudiant
- [x] Modifier un étudiant
- [x] Rechercher un étudiant
- [x] Filtrer par sexe/cohorte
- [x] Exporter en CSV

### ✅ Enseignants
- [x] Voir la liste
- [x] Ajouter un enseignant
- [x] Modifier un enseignant
- [x] Rechercher un enseignant
- [x] Filtrer par grade/fonction
- [x] Exporter en CSV

### ✅ UE
- [x] Voir la liste
- [x] Ajouter une UE
- [x] Modifier une UE
- [x] Rechercher une UE
- [x] Filtrer par semestre
- [x] Dupliquer une UE

### ✅ EC
- [x] Voir la liste
- [x] Ajouter un EC
- [x] Modifier un EC
- [x] Rechercher un EC
- [x] Filtrer par UE
- [x] Exporter en CSV

### ✅ Jurys
- [x] Voir la liste
- [x] Ajouter un jury
- [x] Modifier un jury
- [x] Rechercher un jury
- [x] Filtrer par classe
- [x] Exporter en CSV

---

## 📊 Captures d'Écran Attendues

### Page d'Accueil Admin
```
┌─────────────────────────────────────────┐
│ Administration Système LMD              │
│ Gestion du Système Universitaire LMD   │
├─────────────────────────────────────────┤
│                                         │
│ AUTHENTIFICATION ET AUTORISATION        │
│ • Utilisateurs                          │
│ • Groupes                               │
│                                         │
│ CORE                                    │
│ • Classes                               │
│ • Cohortes                              │
│ • Départements                          │
│ • Éléments Constitutifs (EC)            │
│ • Enseignants                           │
│ • Étudiants                             │
│ • Évaluations                           │
│ • Inscriptions                          │
│ • Jurys                                 │
│ • Sections                              │
│ • Unités d'Enseignement (UE)            │
│                                         │
└─────────────────────────────────────────┘
```

### Liste des Étudiants
```
┌─────────────────────────────────────────────────────────┐
│ Sélectionner Étudiant à modifier                        │
├─────────────────────────────────────────────────────────┤
│ 🔍 Rechercher...                    [Ajouter Étudiant]  │
├─────────────────────────────────────────────────────────┤
│ ☐ Matricule  Nom Complet    Sexe  Cohorte   Téléphone  │
│ ☐ ET2024001  Jean Kabongo   M     L1-2024   +243...    │
│ ☐ ET2024002  Marie Tshala   F     L1-2024   +243...    │
├─────────────────────────────────────────────────────────┤
│ Action: [Exporter CSV ▼] [Exécuter]                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🎬 Scénarios de Test

### Scénario 1 : Créer un Programme Complet
```
1. Créer Section "MATH"
2. Créer Département "MATH-L1"
3. Créer UE "Analyse Mathématique"
4. Créer 2 EC pour cette UE
5. Vérifier la hiérarchie
```

### Scénario 2 : Inscrire un Étudiant
```
1. Créer compte utilisateur (role: ETUDIANT)
2. Créer profil étudiant
3. Créer inscription pour 2024-2025
4. Vérifier dans la liste des inscriptions
```

### Scénario 3 : Constituer un Jury
```
1. Créer compte utilisateur (role: JURY)
2. Créer jury avec composition complète
3. Lier à une classe
4. Vérifier dans la liste des jurys
```

---

## 📈 Résultats Attendus

Après cette démonstration, vous devriez avoir :
- ✅ 2 étudiants dans le système
- ✅ 2 enseignants dans le système
- ✅ 3 UE (dont 1 dupliquée)
- ✅ 3 EC
- ✅ 1 jury configuré
- ✅ Plusieurs fichiers CSV exportés

---

## 🎓 Conclusion

**L'interface d'administration permet de :**
- ✅ Gérer complètement les étudiants
- ✅ Gérer complètement les enseignants
- ✅ Gérer complètement les UE
- ✅ Gérer complètement les EC
- ✅ Gérer complètement les jurys
- ✅ Exporter les données en CSV
- ✅ Rechercher et filtrer facilement
- ✅ Organiser les formulaires de manière intuitive

**Tout est prêt et fonctionnel !** 🚀

---

**Testez maintenant : http://localhost:8000/admin/** 🎉
