# Guide Multi-Institutions — LMD Manager Pro

## Architecture

Chaque institution est une **instance Django indépendante** avec :
- Son propre **sous-domaine** (ex: `ista-gm.lmdmanagerpro.com`)
- Sa propre **base de données MySQL**
- Son propre fichier **`local_settings.py`** (non versionné)
- Le même **code source Git** partagé

```
Code Git (1 repo: batfabonk-lab/lmdmanagerpro)
         │
    ┌────┴────────┐
    ▼             ▼
  ista-gm       ista-casa        (sous-domaines)
    │             │
  DB_istagm     DB_istacasa      (bases MySQL séparées)
    │             │
  local_        local_           (config spécifique)
  settings      settings
```

## Ajouter une nouvelle institution

### 1. Créer le sous-domaine dans cPanel
1. cPanel → **Sous-domaines** (Subdomains)
2. Sous-domaine : `ista-casa` → Domaine : `lmdmanagerpro.com`
3. Racine du document : `/home/tumxxzse/ista-casa`

### 2. Créer la base de données MySQL
1. cPanel → **Bases de données MySQL**
2. Nouvelle base : `tumxxzse_istacasa`
3. L'utilisateur `tumxxzse` a déjà accès (compte principal)

### 3. Créer l'application Python
1. cPanel → **Setup Python App** → Create Application
2. Python version : 3.9
3. Application root : `ista-casa`
4. Application URL : `ista-casa.lmdmanagerpro.com`

### 4. Cloner le repo Git
1. cPanel → **Git Version Control** → Create
2. Clone URL : `https://github.com/batfabonk-lab/lmdmanagerpro.git`
3. Repository Path : `/home/tumxxzse/ista-casa`

### 5. Installer les dépendances
Dans le terminal cPanel (ou via Setup Python App) :
```bash
source /home/tumxxzse/virtualenv/ista-casa/3.9/bin/activate
pip install -r requirements.txt
```

### 6. Créer le local_settings.py
Créer le fichier `/home/tumxxzse/ista-casa/lmdmanagersystem/local_settings.py` :
```python
INSTITUTION_SLUG = 'ista-casa'
INSTITUTION_NAME = 'ISTA Casablanca'
INSTITUTION_DOMAIN = 'ista-casa.lmdmanagerpro.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tumxxzse_istacasa',
        'USER': 'tumxxzse',
        'PASSWORD': 'VOTRE_MOT_DE_PASSE_CPANEL',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

SECRET_KEY = 'GENEREZ_UNE_CLE_UNIQUE_ICI'
DEBUG = False
```

### 7. Configurer le .htaccess
Créer `/home/tumxxzse/ista-casa/.htaccess` (ou dans le dossier public du sous-domaine) :
```
PassengerAppRoot "/home/tumxxzse/ista-casa"
PassengerBaseURI "/"
PassengerPython "/home/tumxxzse/virtualenv/ista-casa/3.9/bin/python"
```

### 8. Lancer les migrations
Réactiver temporairement les URLs de setup dans `urls.py`, puis :
- `https://ista-casa.lmdmanagerpro.com/setup-migrate/?key=lmdsetup2026`

Ou via le terminal cPanel :
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 9. Redémarrer l'app
Setup Python App → Restart

---

## Mettre à jour toutes les institutions

Quand tu modifies le code :

1. **Local** : `git add -A && git commit -m "message" && git push`
2. **Pour chaque institution sur cPanel** :
   - Git Version Control → Manage → Update from Remote
   - Setup Python App → Restart

## Personnaliser par institution

Chaque institution peut avoir ses propres préférences via `local_settings.py` :
- Base de données séparée
- Clé secrète unique
- Fuseau horaire différent
- Fonctionnalités activées/désactivées (à implémenter via les settings)
