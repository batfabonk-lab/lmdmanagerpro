# Système de Gestion Universitaire LMD

Système complet de gestion académique pour les universités suivant le système LMD (Licence-Master-Doctorat).

## Fonctionnalités

### Acteurs
- **Étudiants** : Consultation des notes, inscription, gestion de profil
- **Enseignants** : Encodage des notes, gestion des évaluations
- **Jury** : Délibération et publication des résultats

### Modules
- Gestion des inscriptions
- Gestion pédagogique (Sections, Départements, UE, EC)
- Gestion des évaluations
- Gestion des cohortes
- Délibération et publication des résultats

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
```

2. Activer l'environnement virtuel :
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Appliquer les migrations :
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

6. Lancer le serveur :
```bash
python manage.py runserver
```

## Accès

- Interface d'administration : http://localhost:8000/admin/
- Interface étudiants : http://localhost:8000/etudiant/
- Interface enseignants : http://localhost:8000/enseignant/
- Interface jury : http://localhost:8000/jury/

## Structure du Projet

```
lmdmanager/
├── core/               # Application principale
│   ├── models.py      # Modèles de données
│   ├── views.py       # Vues
│   ├── forms.py       # Formulaires
│   ├── admin.py       # Configuration admin
│   └── urls.py        # URLs
├── templates/         # Templates HTML
├── static/           # Fichiers statiques (CSS, JS)
├── media/            # Fichiers uploadés
└── manage.py         # Script de gestion Django
```

## Technologies

- Django 4.2.7
- Python 3.8+
- SQLite (développement) / PostgreSQL (production)
- Bootstrap 5 (interface utilisateur)
