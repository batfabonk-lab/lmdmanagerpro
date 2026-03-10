# Guide Multi-Institutions — LMD Manager Pro

## Architecture

**Une seule instance Django** gère toutes les institutions via des **URL prefixes** :

- `lmdmanagerpro.com/` → Page de sélection d'institution
- `lmdmanagerpro.com/ista-gm/` → ISTA Gombe
- `lmdmanagerpro.com/ista-casa/` → ISTA Casablanca

Chaque institution a sa propre **base de données MySQL** (isolation totale des données).

```
lmdmanagerpro.com
       │
       ├── /              → Sélecteur d'institution
       ├── /ista-gm/      → BD: tumxxzse_lmdmanager
       └── /ista-casa/    → BD: tumxxzse_istacasa
       
Un seul déploiement, un seul local_settings.py
```

### Comment ça marche

1. `InstitutionMiddleware` extrait le slug de l'URL (`/ista-gm/login/` → slug=`ista-gm`)
2. `set_script_prefix('/ista-gm/')` fait que tous les `{% url %}` incluent le préfixe automatiquement
3. `InstitutionRouter` route les requêtes SQL vers la bonne base de données
4. **Zéro changement** dans les templates, vues, ou URL patterns

---

## Ajouter une nouvelle institution

### 1. Créer la base de données MySQL
1. cPanel → **Bases de données MySQL**
2. Nouvelle base : `tumxxzse_istacasa`
3. L'utilisateur `tumxxzse` a déjà accès (compte principal)

### 2. Modifier le local_settings.py sur le serveur

Éditer `/home/tumxxzse/ista-gm/lmdmanagersystem/local_settings.py` :

```python
INSTITUTIONS = {
    'ista-gm': {
        'name': 'ISTA Gombe',
        'database': 'ista-gm',
    },
    'ista-casa': {                    # ← AJOUTER
        'name': 'ISTA Casablanca',
        'database': 'ista-casa',
    },
}

DATABASES = {
    'default': { ... },              # existant
    'ista-gm': { ... },              # existant
    'ista-casa': {                    # ← AJOUTER
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tumxxzse_istacasa',
        'USER': 'tumxxzse',
        'PASSWORD': 'MOT_DE_PASSE',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
}
```

### 3. Lancer les migrations sur la nouvelle BD

Via le terminal cPanel :
```bash
source /home/tumxxzse/virtualenv/ista-gm/3.9/bin/activate
cd /home/tumxxzse/ista-gm
python manage.py migrate --database=ista-casa
python manage.py createsuperuser --database=ista-casa
```

### 4. Redémarrer l'app
Setup Python App → Restart

### 5. Tester
- `https://lmdmanagerpro.com/` → le sélecteur affiche la nouvelle institution
- `https://lmdmanagerpro.com/ista-casa/` → login de la nouvelle institution

---

## Mettre à jour le code

1. **Local** : `git add -A && git commit -m "message" && git push`
2. **cPanel** : Git Version Control → Update from Remote → Setup Python App → Restart

Pas besoin de toucher à `local_settings.py` sauf si on ajoute/modifie une institution.

## Fichiers clés

| Fichier | Rôle |
|---------|------|
| `lmdmanagersystem/middleware.py` | Routing URL prefix + DB selection |
| `lmdmanagersystem/db_router.py` | Database router multi-BD |
| `lmdmanagersystem/settings.py` | Config par défaut (versionné) |
| `lmdmanagersystem/local_settings.py` | Config serveur : INSTITUTIONS + DATABASES (non versionné) |
| `templates/select_institution.html` | Page de sélection d'institution |
