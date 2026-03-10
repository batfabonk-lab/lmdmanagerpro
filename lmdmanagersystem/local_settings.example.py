"""
Local settings — configuration spécifique au serveur.
Copy this file to local_settings.py and customize.
This file is NOT versioned in Git.

URL: lmdmanagerpro.com/ista-gm/, lmdmanagerpro.com/ista-casa/, etc.
Chaque institution a sa propre base de données MySQL.
"""

# ═══ DOMAINE PRINCIPAL ═══
INSTITUTION_DOMAIN = 'lmdmanagerpro.com'

# ═══ INSTITUTIONS DISPONIBLES ═══
# Clé = slug URL (ex: /ista-gm/), database = clé dans DATABASES ci-dessous
INSTITUTIONS = {
    'ista-gm': {
        'name': 'ISTA Gombe',
        'database': 'ista-gm',
    },
    # Ajouter d'autres institutions :
    # 'ista-casa': {
    #     'name': 'ISTA Casablanca',
    #     'database': 'ista-casa',
    # },
}

# ═══ BASES DE DONNÉES ═══
# 'default' est requis par Django (peut pointer vers la 1ère institution)
# Chaque institution a sa propre BD
_MYSQL_OPTIONS = {
    'charset': 'utf8mb4',
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tumxxzse_lmdmanager',
        'USER': 'tumxxzse',
        'PASSWORD': 'VOTRE_MOT_DE_PASSE',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': _MYSQL_OPTIONS,
    },
    'ista-gm': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tumxxzse_lmdmanager',      # Même BD que default pour la 1ère institution
        'USER': 'tumxxzse',
        'PASSWORD': 'VOTRE_MOT_DE_PASSE',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': _MYSQL_OPTIONS,
    },
    # 'ista-casa': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'tumxxzse_istacasa',       # BD séparée pour cette institution
    #     'USER': 'tumxxzse',
    #     'PASSWORD': 'VOTRE_MOT_DE_PASSE',
    #     'HOST': 'localhost',
    #     'PORT': '3306',
    #     'OPTIONS': _MYSQL_OPTIONS,
    # },
}

# ═══ SÉCURITÉ ═══
SECRET_KEY = 'changez-moi-avec-une-vraie-cle-secrete-unique'
DEBUG = False

# ═══ PRÉFÉRENCES (optionnel) ═══
# TIME_ZONE = 'Africa/Kinshasa'
