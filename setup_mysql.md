# Configuration MySQL pour LMD Manager

## Étapes de migration

### 1. Installation de MySQL
```bash
# Windows : Télécharger et installer MySQL depuis https://dev.mysql.com/downloads/mysql/
# Ubuntu/Debian :
sudo apt update
sudo apt install mysql-server
# macOS :
brew install mysql
```

### 2. Démarrer MySQL
```bash
# Windows : Démarrer le service MySQL
# Ubuntu/Debian :
sudo systemctl start mysql
sudo systemctl enable mysql
# macOS :
brew services start mysql
```

### 3. Créer la base de données
```sql
mysql -u root -p
CREATE DATABASE lmdmanager_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 4. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

### 5. Créer le fichier .env
Copier `.env.example` vers `.env` et configurer :
```bash
DB_NAME=lmdmanager_db
DB_USER=root
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=localhost
DB_PORT=3306
```

### 6. Appliquer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

## Configuration terminée

Le projet utilise maintenant MySQL comme SGBD au lieu de SQLite.
