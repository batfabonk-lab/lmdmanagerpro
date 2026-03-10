"""
Local settings per institution.
Copy this file to local_settings.py and customize for each instance.
This file is NOT versioned in Git.
"""

# ═══ INSTITUTION ═══
INSTITUTION_SLUG = 'ista-gm'           # Identifiant unique (utilisé en interne)
INSTITUTION_NAME = 'ISTA Gombe'        # Nom complet affiché dans l'interface
INSTITUTION_DOMAIN = 'ista-gm.lmdmanagerpro.com'  # Sous-domaine de cette instance

# ═══ BASE DE DONNÉES (propre à chaque institution) ═══
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tumxxzse_istagm',         # Nom de la BD pour cette institution
        'USER': 'tumxxzse',                 # Utilisateur MySQL
        'PASSWORD': 'VOTRE_MOT_DE_PASSE',  # Mot de passe MySQL
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ═══ SÉCURITÉ ═══
SECRET_KEY = 'changez-moi-avec-une-vraie-cle-secrete-unique-par-institution'
DEBUG = False

# ═══ PRÉFÉRENCES INSTITUTION (personnalisables) ═══
# Fuseau horaire
# TIME_ZONE = 'Africa/Kinshasa'

# Année académique par défaut
# DEFAULT_ANNEE_ACADEMIQUE = '2025-2026'

# Activer/désactiver des fonctionnalités
# COMPENSATION_ACTIVE = True
# RATTRAPAGE_AUTORISE = True
# RACHAT_AUTORISE = True
# SEUIL_VALIDATION = 10
# SEUIL_COMPENSATION = 8
