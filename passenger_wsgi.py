import os
import sys

# Chemin vers le répertoire du projet Django
# cPanel user: tumxxzse | domaine: lmdmanagerpro.com
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Ajout du projet au PYTHONPATH
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Chemin vers l'environnement virtuel cPanel
# Le chemin exact sera créé par Setup Python App dans cPanel
# Vérifiez la version Python dans votre cPanel et adaptez si nécessaire
VENV_DIR = os.path.join('/home/tumxxzse/virtualenv/ista-gm', '3.9')
VENV_SITE_PACKAGES = None

# Recherche automatique du dossier site-packages dans le venv
for root, dirs, files in os.walk(os.path.join(VENV_DIR, 'lib')):
    if 'site-packages' in dirs:
        VENV_SITE_PACKAGES = os.path.join(root, 'site-packages')
        break

if VENV_SITE_PACKAGES and VENV_SITE_PACKAGES not in sys.path:
    sys.path.insert(0, VENV_SITE_PACKAGES)

os.environ['DJANGO_SETTINGS_MODULE'] = 'lmdmanagersystem.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
