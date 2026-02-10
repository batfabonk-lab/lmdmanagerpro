# 🏗️ Architecture du Système LMD

## Vue d'Ensemble

Le système suit l'architecture **MVT (Model-View-Template)** de Django avec une séparation claire des responsabilités.

---

## 📊 Diagramme de l'Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    UTILISATEURS                          │
│  (Étudiant, Enseignant, Jury, Admin)                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  COUCHE PRÉSENTATION                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Templates HTML + Bootstrap 5                     │  │
│  │  - base.html (template parent)                    │  │
│  │  - home.html, login.html                          │  │
│  │  - etudiant/, enseignant/, jury/                  │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   COUCHE CONTRÔLEUR                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Views (core/views.py)                            │  │
│  │  - home(), login_view(), logout_view()            │  │
│  │  - etudiant_dashboard(), etudiant_notes()         │  │
│  │  - enseignant_dashboard(), encoder_notes()        │  │
│  │  - jury_dashboard(), deliberer(), publier()       │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  URLs (core/urls.py + lmdmanagersystem/urls.py)  │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    COUCHE MÉTIER                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Models (core/models.py)                          │  │
│  │  - User (authentification)                        │  │
│  │  - Etudiant, Enseignant, Jury                     │  │
│  │  - UE, EC, Evaluation                             │  │
│  │  - Inscription, Cohorte, Classe                   │  │
│  │  - Section, Departement                           │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Logique Métier                                   │  │
│  │  - calculer_note_finale()                         │  │
│  │  - valider_statut()                               │  │
│  │  - Décisions automatiques du jury                 │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  COUCHE DONNÉES                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ORM Django                                       │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Base de Données SQLite (dev)                     │  │
│  │  PostgreSQL (production recommandée)              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂️ Structure des Modèles

### Hiérarchie des Relations

```
Section
  └── Departement
        └── Enseignant

UE
  └── EC
        └── Evaluation
              ├── Etudiant
              └── UE

Cohorte
  └── Etudiant
        └── Inscription
              └── Classe
                    └── Jury

User (authentification)
  ├── Etudiant
  ├── Enseignant
  └── Jury
```

---

## 🔄 Flux de Données

### 1. Authentification
```
Utilisateur → login_view() → authenticate() → User.role
                                                    ↓
                        ┌──────────────────────────┼──────────────────────────┐
                        ▼                          ▼                          ▼
                  ETUDIANT                   ENSEIGNANT                     JURY
                        ↓                          ↓                          ▼
            etudiant_dashboard()       enseignant_dashboard()      jury_dashboard()
```

### 2. Consultation des Notes (Étudiant)
```
Étudiant → etudiant_notes()
              ↓
         Evaluation.objects.filter(matricule_et=etudiant)
              ↓
         calculer_note_finale() pour chaque évaluation
              ↓
         Organiser par UE
              ↓
         Afficher dans template
```

### 3. Encodage des Notes (Enseignant)
```
Enseignant → enseignant_encoder_notes()
                ↓
           Afficher toutes les évaluations
                ↓
           Formulaire modal pour chaque évaluation
                ↓
           POST: Mise à jour CC, Examen, Rattrapage, Rachat
                ↓
           evaluation.save() → Trigger valider_statut()
                ↓
           Calcul automatique du statut (VALIDE/NON_VALIDE)
```

### 4. Délibération (Jury)
```
Jury → jury_deliberer()
          ↓
     Récupérer inscriptions de la classe
          ↓
     Pour chaque étudiant:
          ├── Récupérer évaluations
          ├── Calculer moyenne générale
          └── Déterminer décision (Admis/Ajourné)
          ↓
     Afficher tableau des résultats
```

---

## 🔐 Système de Sécurité

### Niveaux de Protection

```
1. AUTHENTIFICATION
   └── @login_required sur toutes les vues protégées
       └── Redirection vers /login/ si non authentifié

2. AUTORISATION
   └── Vérification du rôle dans chaque vue
       ├── if user.role == 'ETUDIANT'
       ├── if user.role == 'ENSEIGNANT'
       └── if user.role == 'JURY'

3. PROTECTION CSRF
   └── {% csrf_token %} dans tous les formulaires

4. VALIDATION
   └── Validators dans les modèles
       ├── MinValueValidator(0)
       ├── MaxValueValidator(20)
       └── unique_together
```

---

## 📦 Organisation des Fichiers

### Application Core

```
core/
├── __init__.py
├── admin.py              # Configuration admin
│   ├── UserAdmin
│   ├── EtudiantAdmin
│   ├── EnseignantAdmin
│   ├── JuryAdmin
│   └── EvaluationAdmin (+ 7 autres)
│
├── models.py             # Modèles de données
│   ├── User (AbstractUser)
│   ├── Section, Departement
│   ├── UE, EC
│   ├── Cohorte, Classe
│   ├── Etudiant, Enseignant, Jury
│   ├── Inscription
│   └── Evaluation
│
├── views.py              # Logique métier
│   ├── home()
│   ├── login_view(), logout_view()
│   ├── etudiant_dashboard(), etudiant_notes()
│   ├── enseignant_dashboard(), encoder_notes()
│   └── jury_dashboard(), deliberer(), publier()
│
├── urls.py               # Routes
│   └── 13 URLs définies
│
└── migrations/           # Migrations de BDD
    └── 0001_initial.py
```

### Templates

```
templates/
├── base.html                    # Template parent
│   ├── Navbar
│   ├── Sidebar (si authentifié)
│   ├── Messages
│   └── Content block
│
├── home.html                    # Page d'accueil
├── login.html                   # Connexion
│
├── etudiant/
│   ├── dashboard.html           # Tableau de bord
│   └── notes.html               # Consultation notes
│
├── enseignant/
│   ├── dashboard.html           # Tableau de bord
│   └── encoder_notes.html       # Encodage notes
│
└── jury/
    ├── dashboard.html           # Tableau de bord
    ├── deliberer.html           # Délibération
    └── publier.html             # Publication
```

---

## 🎯 Patterns de Conception Utilisés

### 1. MVT (Model-View-Template)
- **Model** : Logique de données et métier
- **View** : Contrôleurs et logique de présentation
- **Template** : Présentation HTML

### 2. DRY (Don't Repeat Yourself)
- Template de base réutilisable
- Méthodes dans les modèles
- Décorateurs pour l'authentification

### 3. Fat Models, Thin Views
- Logique métier dans les modèles
- Vues simples et lisibles
- Méthodes comme `calculer_note_finale()`

### 4. Template Inheritance
- `base.html` comme parent
- Blocks réutilisables
- Sidebar conditionnelle

---

## 🔧 Configuration

### Settings Principaux

```python
# lmdmanagersystem/settings.py

INSTALLED_APPS = [
    'core',                    # Application principale
    ...
]

AUTH_USER_MODEL = 'core.User'  # Modèle utilisateur personnalisé

TEMPLATES = [{
    'DIRS': [BASE_DIR / 'templates'],  # Templates globaux
    ...
}]

LANGUAGE_CODE = 'fr-fr'        # Français
TIME_ZONE = 'Africa/Kinshasa'  # Fuseau horaire RDC

MEDIA_URL = '/media/'          # Fichiers uploadés
STATIC_URL = '/static/'        # Fichiers statiques
```

---

## 📊 Base de Données

### Schéma Relationnel

```sql
-- Tables principales avec relations

User (id, username, password, role)
  ↓ OneToOne
Etudiant (matricule_et, nom_complet, ..., id_lgn_id)
  ↓ ForeignKey
Inscription (id, annee_academique, matricule_et_id, ...)
  ↓ ForeignKey
Evaluation (id_ev, cc, examen, ..., matricule_et_id, code_ue_id, code_ec_id)

-- Contraintes
UNIQUE (matricule_et, code_ue, code_ec) sur Evaluation
UNIQUE (annee_academique, matricule_et) sur Inscription
```

---

## 🚀 Performance

### Optimisations Implémentées

1. **select_related()** - Jointures SQL optimisées
   ```python
   Evaluation.objects.select_related('matricule_et', 'code_ue', 'code_ec')
   ```

2. **Indexation** - Clés primaires et étrangères indexées automatiquement

3. **Calculs côté serveur** - Notes calculées en Python, pas en SQL

4. **Templates cachés** - Django met en cache les templates compilés

---

## 📈 Évolutivité

### Points d'Extension

1. **Nouveaux Rôles**
   - Ajouter dans `User.ROLE_CHOICES`
   - Créer vues et templates correspondants

2. **Nouvelles Fonctionnalités**
   - Ajouter modèles dans `models.py`
   - Créer vues dans `views.py`
   - Ajouter routes dans `urls.py`

3. **API REST**
   - Installer Django REST Framework
   - Créer serializers
   - Ajouter viewsets

4. **Multi-tenancy**
   - Ajouter modèle `Etablissement`
   - Filtrer par établissement
   - Isoler les données

---

## 🎓 Conclusion

L'architecture est :
- ✅ **Modulaire** - Séparation claire des responsabilités
- ✅ **Évolutive** - Facile à étendre
- ✅ **Maintenable** - Code organisé et documenté
- ✅ **Performante** - Optimisations en place
- ✅ **Sécurisée** - Authentification et autorisation

**Architecture prête pour la production avec quelques ajustements (PostgreSQL, Redis, etc.)** 🚀
