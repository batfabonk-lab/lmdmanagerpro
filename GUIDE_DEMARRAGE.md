# Guide de Démarrage Rapide - Système LMD

## 🚀 Démarrage Rapide

### 1. Lancer le serveur
```bash
python manage.py runserver
```

### 2. Accéder à l'application
- **Interface principale** : http://localhost:8000/
- **Interface d'administration** : http://localhost:8000/admin/

## 👥 Comptes de Test

### Administrateur
- **Username** : `admin`
- **Password** : `admin123`
- **Accès** : Interface d'administration complète

### Étudiant
- **Username** : `etudiant1`
- **Password** : `etudiant123`
- **Fonctionnalités** :
  - Consulter ses notes
  - Voir ses inscriptions
  - Consulter sa moyenne générale

### Enseignant
- **Username** : `enseignant1`
- **Password** : `enseignant123`
- **Fonctionnalités** :
  - Encoder les notes des étudiants
  - Modifier les évaluations (CC, Examen, Rattrapage, Rachat)
  - Voir les statistiques

### Jury
- **Username** : `jury1`
- **Password** : `jury123`
- **Fonctionnalités** :
  - Délibérer sur les résultats
  - Publier les résultats officiels
  - Voir la liste des étudiants de la classe

## 📋 Fonctionnalités Principales

### Pour les Étudiants
1. **Tableau de bord** : Vue d'ensemble des informations personnelles
2. **Mes Notes** : Consultation détaillée des notes par UE et EC
3. **Moyenne Générale** : Calcul automatique de la moyenne

### Pour les Enseignants
1. **Tableau de bord** : Statistiques sur les évaluations
2. **Encoder Notes** : Interface pour saisir et modifier les notes
3. **Validation automatique** : Le système calcule automatiquement le statut (Validé/Non validé)

### Pour le Jury
1. **Tableau de bord** : Liste des étudiants de la classe
2. **Délibération** : Vue des moyennes et décisions automatiques
3. **Publication** : Publication officielle des résultats

## 🎯 Flux de Travail Typique

### 1. Inscription d'un Étudiant (Admin)
```
Admin → Créer Utilisateur (rôle: ETUDIANT)
     → Créer Profil Étudiant
     → Créer Inscription
```

### 2. Encodage des Notes (Enseignant)
```
Enseignant → Se connecter
          → Encoder Notes
          → Saisir CC et Examen
          → (Optionnel) Rattrapage/Rachat
          → Enregistrer
```

### 3. Consultation (Étudiant)
```
Étudiant → Se connecter
        → Mes Notes
        → Voir les notes par UE
```

### 4. Délibération (Jury)
```
Jury → Se connecter
    → Délibérer
    → Voir les moyennes et décisions
    → Publier Résultats
```

## 🔧 Commandes Utiles

### Créer un nouveau superutilisateur
```bash
python manage.py createsuperuser
```

### Créer des données de test
```bash
python create_test_data.py
```

### Appliquer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecter les fichiers statiques (production)
```bash
python manage.py collectstatic
```

## 📊 Structure de la Base de Données

### Modèles Principaux
- **User** : Utilisateurs du système (avec rôles)
- **Etudiant** : Profils étudiants
- **Enseignant** : Profils enseignants
- **Jury** : Jurys de délibération
- **UE** : Unités d'Enseignement
- **EC** : Éléments Constitutifs
- **Evaluation** : Notes et évaluations
- **Inscription** : Inscriptions annuelles
- **Cohorte** : Promotions d'étudiants
- **Classe** : Classes/groupes

## 🎨 Interface Utilisateur

L'interface utilise :
- **Bootstrap 5** : Framework CSS moderne
- **Bootstrap Icons** : Icônes
- **Design responsive** : Compatible mobile et desktop
- **Thème moderne** : Interface claire et intuitive

## 📝 Calcul des Notes

### Formule de la Note Finale
```
Note Finale = (CC × 0.4) + (Examen × 0.6)

Si Rattrapage existe:
  Note Finale = max(Note Finale, Rattrapage)

Si Rachat existe:
  Note Finale = Rachat
```

### Statut de Validation
- **Validé** : Note Finale ≥ 10/20
- **Non validé** : Note Finale < 10/20

### Décisions du Jury
- **Admis** : Moyenne ≥ 12/20
- **Admis avec mention passable** : 10 ≤ Moyenne < 12
- **Ajourné** : Moyenne < 10/20

## 🔐 Sécurité

- Authentification requise pour toutes les pages (sauf accueil et login)
- Séparation des rôles (Étudiant, Enseignant, Jury, Admin)
- Redirection automatique selon le rôle
- Protection CSRF sur tous les formulaires

## 🌐 URLs Principales

```
/                          → Page d'accueil
/login/                    → Connexion
/logout/                   → Déconnexion
/admin/                    → Interface d'administration

/etudiant/                 → Tableau de bord étudiant
/etudiant/notes/           → Notes de l'étudiant

/enseignant/               → Tableau de bord enseignant
/enseignant/encoder/       → Encoder les notes

/jury/                     → Tableau de bord jury
/jury/deliberer/           → Délibération
/jury/publier/             → Publication des résultats
```

## 📞 Support

Pour toute question ou problème :
1. Vérifiez que le serveur est lancé
2. Vérifiez les migrations sont appliquées
3. Consultez les logs dans le terminal
4. Vérifiez que les données de test sont créées

## 🎓 Prochaines Étapes

1. **Personnaliser** : Adapter les modèles à vos besoins
2. **Ajouter des fonctionnalités** : Bulletins PDF, statistiques avancées, etc.
3. **Déployer** : Configurer pour la production (PostgreSQL, Gunicorn, Nginx)
4. **Sécuriser** : Configurer HTTPS, variables d'environnement, etc.

---

**Bon développement ! 🚀**
