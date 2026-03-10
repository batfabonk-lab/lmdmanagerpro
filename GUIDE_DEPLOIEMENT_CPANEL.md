# Guide de Déploiement cPanel - LMD Manager Pro

## Prérequis
- Un hébergement cPanel avec **Python Selector** (CloudLinux) ou **Setup Python App**
- Accès SSH (recommandé) ou Terminal cPanel
- MySQL disponible sur le cPanel

---

## Étape 1 : Créer la base de données MySQL sur cPanel

1. Connectez-vous à votre **cPanel**
2. Allez dans **Bases de données MySQL**
3. Créez une nouvelle base de données : `tumxxzse_lmdmanager`
4. Créez un utilisateur MySQL avec un mot de passe fort
5. Associez l'utilisateur à la base de données avec **TOUS LES PRIVILEGES**

> **Note** : Sur cPanel, le nom de la BD est préfixé par votre username cPanel.
> Votre user cPanel est `tumxxzse`, donc la BD sera `tumxxzse_lmdmanager`

---

## Étape 2 : Créer l'application Python sur cPanel

1. Dans cPanel, allez dans **Setup Python App** (ou Python Selector)
2. Cliquez sur **CREATE APPLICATION**
3. Configurez :
   - **Python version** : `3.9` ou `3.10` ou `3.11` (choisir la plus récente disponible)
   - **Application root** : `lmdmanager` (le dossier où sera votre projet)
   - **Application URL** : `lmdmanagerpro.com`
   - **Application startup file** : `passenger_wsgi.py`
   - **Application Entry point** : `application`
4. Cliquez sur **CREATE**

> **Important** : Notez le chemin du virtualenv créé automatiquement par cPanel.
> Il ressemblera à : `/home/tumxxzse/virtualenv/ista-gm/3.x/`

---

## Étape 3 : Transférer les fichiers du projet

### Option A : Via le File Manager cPanel
1. Compressez votre projet en `.zip` (sans le dossier `venv/`, `__pycache__/`, `db.sqlite3`)
2. Dans File Manager, naviguez vers `/home/tumxxzse/ista-gm/`
3. Uploadez et extrayez le `.zip`

### Option B : Via Git (recommandé)
```bash
# En SSH sur le serveur
cd /home/tumxxzse/ista-gm
git clone VOTRE_REPO_GIT .
```

### Option C : Via FTP/SFTP
Utilisez FileZilla ou WinSCP pour transférer les fichiers vers `/home/tumxxzse/ista-gm/`

### Fichiers à NE PAS transférer :
- `venv/` (l'environnement virtuel sera créé sur le serveur)
- `__pycache__/`
- `db.sqlite3`
- `.git/` (sauf si vous utilisez Git)
- Les fichiers `*.pyc`

---

## Étape 4 : Installer les dépendances

Dans le Terminal cPanel ou en SSH :

```bash
# Activez le virtualenv créé par cPanel (la commande exacte est affichée 
# dans Setup Python App, copiez-la)
source /home/tumxxzse/virtualenv/ista-gm/3.9/bin/activate

# Allez dans le dossier du projet
cd /home/tumxxzse/ista-gm

# Installez les dépendances
pip install -r requirements.txt
```

> **Note** : Si `mysqlclient` échoue à l'installation, `PyMySQL` suffira car il est
> déjà configuré dans le projet comme remplacement.

---

## Étape 5 : Configurer les variables d'environnement

Dans cPanel > **Setup Python App** > votre application > **Environment variables**, ajoutez :

| Variable | Valeur |
|---|---|
| `ON_CPANEL` | `True` |
| `CPANEL_DOMAIN` | `lmdmanagerpro.com` |
| `DJANGO_SECRET_KEY` | (générez une clé secrète unique, voir ci-dessous) |
| `DB_NAME` | `tumxxzse_lmdmanager` |
| `DB_USER` | `tumxxzse` (ou l'utilisateur DB créé à l'étape 1) |
| `DB_PASSWORD` | `votre_mot_de_passe_db` |
| `DB_HOST` | `localhost` |

### Générer une SECRET_KEY :
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Étape 6 : Configurer passenger_wsgi.py

Ouvrez `/home/tumxxzse/ista-gm/passenger_wsgi.py` et vérifiez que les chemins sont corrects.

Le fichier est déjà configuré pour détecter automatiquement les chemins, mais si vous avez des problèmes, adaptez manuellement :

```python
# Le chemin est déjà configuré pour votre compte :
VENV_DIR = '/home/tumxxzse/virtualenv/ista-gm/3.9'
```

---

## Étape 7 : Migrations et fichiers statiques

En SSH ou Terminal cPanel (avec le virtualenv activé) :

```bash
cd /home/tumxxzse/ista-gm

# Exécuter les migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Créer un super utilisateur (si nouveau déploiement)
python manage.py createsuperuser
```

---

## Étape 8 : Configurer les fichiers statiques

Dans cPanel > **Setup Python App**, ajoutez des **Static files mappings** :

| URL | Directory |
|---|---|
| `/static/` | `/home/tumxxzse/ista-gm/staticfiles` |
| `/media/` | `/home/tumxxzse/ista-gm/media` |

---

## Étape 9 : Redémarrer l'application

1. Dans **Setup Python App**, cliquez sur **RESTART** pour votre application
2. Visitez votre domaine pour vérifier que tout fonctionne

---

## Dépannage

### Erreur 500
- Vérifiez les logs dans : `/home/tumxxzse/logs/error.log`
- Vérifiez que les variables d'environnement sont correctes
- Vérifiez que le virtualenv contient tous les packages

### Page blanche
- Vérifiez que `passenger_wsgi.py` a les bons chemins
- Redémarrez l'application dans Setup Python App

### Erreur de base de données
- Vérifiez le nom de la BD (préfixé par le user cPanel)
- Vérifiez les privilèges de l'utilisateur MySQL
- Testez la connexion en SSH : `python manage.py dbshell`

### Fichiers statiques non chargés (CSS/JS)
- Vérifiez que `collectstatic` a été exécuté
- Vérifiez les mappings de fichiers statiques dans Setup Python App
- Le dossier `staticfiles/` doit exister et contenir les fichiers

### mysqlclient ne s'installe pas
- PyMySQL est déjà configuré comme alternative, ce n'est pas bloquant
- Si nécessaire, commentez `mysqlclient` dans `requirements.txt`

---

## Résumé des fichiers modifiés/créés pour cPanel

| Fichier | Description |
|---|---|
| `passenger_wsgi.py` | Point d'entrée WSGI pour Passenger (cPanel) |
| `.htaccess` | Configuration Apache pour le routage |
| `lmdmanagersystem/settings.py` | Ajout détection cPanel + config DB cPanel |
| `GUIDE_DEPLOIEMENT_CPANEL.md` | Ce guide |
