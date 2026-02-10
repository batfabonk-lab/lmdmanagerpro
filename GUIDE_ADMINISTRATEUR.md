# 👨‍💼 Guide de l'Administrateur - Système LMD

## 🔐 Accès à l'Administration

### Connexion
- **URL** : http://localhost:8000/admin/
- **Compte Admin** : `admin` / `admin123`

---

## 📋 Fonctionnalités de Gestion

### 1️⃣ Gestion des Étudiants

**Accès** : Admin → Core → Étudiants

#### Fonctionnalités Disponibles
- ✅ **Ajouter** un nouvel étudiant
- ✅ **Modifier** les informations d'un étudiant
- ✅ **Supprimer** un étudiant
- ✅ **Rechercher** par matricule, nom ou téléphone
- ✅ **Filtrer** par sexe, cohorte ou nationalité
- ✅ **Exporter** la liste en CSV

#### Comment Ajouter un Étudiant

1. Cliquez sur **"Ajouter Étudiant"**
2. Remplissez les informations :
   - **Informations Personnelles** :
     - Matricule (ex: ET2024002)
     - Nom complet
     - Sexe (M/F)
     - Date de naissance
     - Nationalité
   - **Contact** :
     - Téléphone
     - Photo (optionnel)
   - **Informations Académiques** :
     - Cohorte
     - Compte utilisateur (créer d'abord dans Users)
3. Cliquez sur **"Enregistrer"**

#### Export CSV
1. Sélectionnez les étudiants à exporter (cochez les cases)
2. Dans "Action", choisissez **"Exporter les étudiants sélectionnés (CSV)"**
3. Cliquez sur **"Exécuter"**
4. Le fichier `etudiants.csv` sera téléchargé

---

### 2️⃣ Gestion des Enseignants

**Accès** : Admin → Core → Enseignants

#### Fonctionnalités Disponibles
- ✅ **Ajouter** un nouvel enseignant
- ✅ **Modifier** les informations d'un enseignant
- ✅ **Supprimer** un enseignant
- ✅ **Rechercher** par matricule, nom ou téléphone
- ✅ **Filtrer** par grade, fonction ou département
- ✅ **Exporter** la liste en CSV

#### Comment Ajouter un Enseignant

1. Cliquez sur **"Ajouter Enseignant"**
2. Remplissez les informations :
   - **Informations Personnelles** :
     - Matricule (ex: EN2024002)
     - Nom complet
     - Téléphone
     - Photo (optionnel)
   - **Informations Professionnelles** :
     - Grade (ex: Professeur, Chargé de cours, Assistant)
     - Fonction (ex: Enseignant-Chercheur, Enseignant)
     - Département
   - **Compte Utilisateur** :
     - Sélectionner le compte (créer d'abord dans Users)
3. Cliquez sur **"Enregistrer"**

#### Grades Suggérés
- Professeur Ordinaire
- Professeur Associé
- Chargé de Cours
- Chef de Travaux
- Assistant

---

### 3️⃣ Gestion des UE (Unités d'Enseignement)

**Accès** : Admin → Core → Unités d'Enseignement

#### Fonctionnalités Disponibles
- ✅ **Ajouter** une nouvelle UE
- ✅ **Modifier** une UE existante
- ✅ **Supprimer** une UE
- ✅ **Rechercher** par code ou intitulé
- ✅ **Filtrer** par semestre ou TP/TD
- ✅ **Dupliquer** une UE

#### Comment Ajouter une UE

1. Cliquez sur **"Ajouter Unité d'Enseignement"**
2. Remplissez les informations :
   - **Informations de Base** :
     - Code UE (ex: UE103)
     - Intitulé (ex: "Algorithmique et Structures de Données")
   - **Détails Académiques** :
     - Crédits (ex: 6)
     - CMI (Charge de travail en heures, ex: 60)
     - TP/TD (ex: TP, TD, ou Cours)
     - Semestre (1 à 10)
3. Cliquez sur **"Enregistrer"**

#### Dupliquer une UE
1. Sélectionnez la/les UE à dupliquer
2. Dans "Action", choisissez **"Dupliquer les UE sélectionnées"**
3. Cliquez sur **"Exécuter"**
4. Une copie sera créée avec "_COPIE" ajouté au code

---

### 4️⃣ Gestion des EC (Éléments Constitutifs)

**Accès** : Admin → Core → Éléments Constitutifs

#### Fonctionnalités Disponibles
- ✅ **Ajouter** un nouvel EC
- ✅ **Modifier** un EC existant
- ✅ **Supprimer** un EC
- ✅ **Rechercher** par code ou intitulé
- ✅ **Filtrer** par UE ou TP/TD
- ✅ **Exporter** la liste en CSV

#### Comment Ajouter un EC

1. Cliquez sur **"Ajouter Élément Constitutif"**
2. Remplissez les informations :
   - **Informations de Base** :
     - Code EC (ex: EC103)
     - Intitulé (ex: "Algorithmes de tri")
     - UE parente (sélectionner dans la liste)
   - **Détails Académiques** :
     - Crédits (ex: 3)
     - CMI (ex: 30)
     - TP/TD (ex: TP)
3. Cliquez sur **"Enregistrer"**

#### Relation UE-EC
- Une **UE** peut contenir **plusieurs EC**
- Chaque **EC** appartient à **une seule UE**
- Les crédits des EC s'additionnent pour former les crédits de l'UE

---

### 5️⃣ Gestion des Jurys

**Accès** : Admin → Core → Jurys

#### Fonctionnalités Disponibles
- ✅ **Ajouter** un nouveau jury
- ✅ **Modifier** un jury existant
- ✅ **Supprimer** un jury
- ✅ **Rechercher** par code, président, secrétaire ou membre
- ✅ **Filtrer** par classe
- ✅ **Exporter** la liste en CSV

#### Comment Ajouter un Jury

1. Cliquez sur **"Ajouter Jury"**
2. Remplissez les informations :
   - **Informations du Jury** :
     - Code Jury (ex: JURY-L1-2025)
     - Classe (sélectionner)
   - **Composition** :
     - Président (nom complet)
     - Secrétaire (nom complet)
     - Membre (nom complet)
   - **Décision** :
     - Laissez vide (sera rempli après délibération)
   - **Compte Utilisateur** :
     - Sélectionner le compte (créer d'abord dans Users)
3. Cliquez sur **"Enregistrer"**

#### Composition du Jury
Un jury est composé de :
- **1 Président** - Dirige la délibération
- **1 Secrétaire** - Prend les notes
- **1 Membre** - Participe à la délibération

---

## 🔧 Gestion des Autres Entités

### Sections
**Accès** : Admin → Core → Sections
- Créer des sections académiques (ex: Informatique, Mathématiques)

### Départements
**Accès** : Admin → Core → Départements
- Créer des départements rattachés aux sections

### Cohortes
**Accès** : Admin → Core → Cohortes
- Créer des promotions d'étudiants (ex: L1-2024)

### Classes
**Accès** : Admin → Core → Classes
- Créer des groupes/classes (ex: L1-INFO-A)

### Inscriptions
**Accès** : Admin → Core → Inscriptions
- Inscrire des étudiants dans des classes pour une année académique

### Évaluations
**Accès** : Admin → Core → Évaluations
- Gérer les notes (CC, Examen, Rattrapage, Rachat)
- Le statut se calcule automatiquement

---

## 👥 Gestion des Utilisateurs

**Accès** : Admin → Authentification et autorisation → Utilisateurs

### Créer un Nouvel Utilisateur

1. Cliquez sur **"Ajouter Utilisateur"**
2. Entrez :
   - Nom d'utilisateur
   - Mot de passe (2 fois)
3. Cliquez sur **"Enregistrer et continuer les modifications"**
4. Remplissez les informations supplémentaires :
   - Email
   - Prénom / Nom
   - **Rôle** (ETUDIANT, ENSEIGNANT, JURY, ADMIN)
   - Statut (Actif, Staff, Superutilisateur)
5. Cliquez sur **"Enregistrer"**

### Rôles Disponibles
- **ETUDIANT** - Accès à l'espace étudiant
- **ENSEIGNANT** - Accès à l'espace enseignant
- **JURY** - Accès à l'espace jury
- **ADMIN** - Accès à l'administration

---

## 📊 Workflow Complet

### Créer un Étudiant Complet

```
1. Créer un Utilisateur
   → Username: etudiant2
   → Password: ****
   → Role: ETUDIANT

2. Créer une Cohorte (si nécessaire)
   → Code: L1-2025
   → Libellé: Licence 1 - Promotion 2025

3. Créer une Classe (si nécessaire)
   → Code: L1-INFO-B
   → Désignation: Licence 1 Informatique - Groupe B

4. Créer le Profil Étudiant
   → Matricule: ET2025001
   → Nom: Marie Tshala
   → Cohorte: L1-2025
   → Compte: etudiant2

5. Créer une Inscription
   → Étudiant: ET2025001
   → Année: 2024-2025
   → Classe: L1-INFO-B
   → Cohorte: L1-2025
```

### Créer un Enseignant Complet

```
1. Créer un Utilisateur
   → Username: enseignant2
   → Password: ****
   → Role: ENSEIGNANT

2. Créer un Département (si nécessaire)
   → Code: MATH-L1
   → Désignation: Mathématiques Licence 1

3. Créer le Profil Enseignant
   → Matricule: EN2025001
   → Nom: Dr. Joseph Mukendi
   → Grade: Chargé de Cours
   → Département: MATH-L1
   → Compte: enseignant2
```

---

## 📈 Statistiques et Rapports

### Tableau de Bord Admin
Le tableau de bord affiche :
- Nombre total d'utilisateurs
- Nombre d'étudiants
- Nombre d'enseignants
- Nombre de jurys
- Nombre d'UE et EC
- Nombre d'évaluations

### Exports Disponibles
- **Étudiants** → CSV
- **Enseignants** → CSV
- **EC** → CSV
- **Jurys** → CSV

---

## 🔍 Recherche et Filtres

### Recherche Globale
Utilisez la barre de recherche en haut à droite pour rechercher dans tous les modèles.

### Recherche par Modèle
Chaque liste a sa propre barre de recherche :
- **Étudiants** : Par matricule, nom, téléphone
- **Enseignants** : Par matricule, nom, téléphone
- **UE** : Par code, intitulé
- **EC** : Par code, intitulé
- **Jurys** : Par code, président, secrétaire, membre

### Filtres Latéraux
Utilisez les filtres sur le côté droit pour affiner les résultats :
- **Étudiants** : Sexe, Cohorte, Nationalité
- **Enseignants** : Grade, Fonction, Département
- **UE** : Semestre, TP/TD
- **EC** : UE, TP/TD
- **Jurys** : Classe

---

## ⚠️ Bonnes Pratiques

### Avant de Supprimer
- ⚠️ **Vérifiez les dépendances** - Un étudiant avec des évaluations ne peut pas être supprimé
- ⚠️ **Faites un export** - Exportez les données avant suppression
- ⚠️ **Utilisez la désactivation** - Préférez désactiver un compte plutôt que le supprimer

### Sécurité
- 🔐 **Changez le mot de passe admin** par défaut
- 🔐 **Créez des comptes staff** pour les autres administrateurs
- 🔐 **Ne partagez pas** les identifiants admin

### Organisation
- 📁 **Créez d'abord** les structures (Sections, Départements, Cohortes, Classes)
- 📁 **Puis créez** les utilisateurs et profils
- 📁 **Enfin créez** les inscriptions et évaluations

---

## 🆘 Dépannage

### Problème : "Impossible de supprimer un étudiant"
**Solution** : L'étudiant a des évaluations ou inscriptions. Supprimez-les d'abord.

### Problème : "Compte utilisateur non trouvé"
**Solution** : Créez d'abord le compte dans Users, puis créez le profil (Étudiant/Enseignant/Jury).

### Problème : "Erreur d'intégrité"
**Solution** : Vérifiez que tous les champs obligatoires sont remplis et que les codes sont uniques.

---

## 📞 Support

Pour toute question :
1. Consultez ce guide
2. Vérifiez les logs dans le terminal
3. Testez avec les données de test

---

**L'interface d'administration est votre outil principal pour gérer tout le système LMD !** 🎓
