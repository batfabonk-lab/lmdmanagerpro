"""Vue temporaire pour exécuter les migrations depuis le navigateur.
SUPPRIMER CE FICHIER après le déploiement!"""
import io
from django.http import HttpResponse
from django.core.management import call_command
from django.conf import settings as django_settings


def diagnose(request):
    """Diagnostic de la connexion MySQL."""
    secret = request.GET.get('key', '')
    if secret != 'lmdsetup2026':
        return HttpResponse("Accès refusé.", status=403)

    results = []
    results.append("=" * 50)
    results.append("DIAGNOSTIC MySQL")
    results.append("=" * 50)

    # Afficher les credentials utilisés par Django
    db = django_settings.DATABASES.get('default', {})
    results.append(f"\nDjango DB config:")
    results.append(f"  ENGINE:   {db.get('ENGINE', '?')}")
    results.append(f"  NAME:     {db.get('NAME', '?')}")
    results.append(f"  USER:     {db.get('USER', '?')}")
    pwd = db.get('PASSWORD', '')
    results.append(f"  PASSWORD: {pwd[:3]}***{pwd[-3:]} (longueur: {len(pwd)})")
    results.append(f"  HOST:     {db.get('HOST', '?')}")
    results.append(f"  PORT:     {db.get('PORT', '?')}")

    results.append(f"\nON_CPANEL: {getattr(django_settings, 'ON_CPANEL', '?')}")
    results.append(f"DEBUG:     {django_settings.DEBUG}")

    # Test connexion directe avec pymysql
    results.append("\n--- Test connexion pymysql directe ---")
    try:
        import pymysql
        conn = pymysql.connect(
            host=db.get('HOST', 'localhost'),
            user=db.get('USER', ''),
            password=db.get('PASSWORD', ''),
            database=db.get('NAME', ''),
            port=int(db.get('PORT', 3306)),
        )
        results.append("✓ Connexion pymysql réussie!")
        conn.close()
    except Exception as e:
        results.append(f"✗ Connexion pymysql échouée: {e}")

    return HttpResponse("\n".join(results), content_type="text/plain; charset=utf-8")


def run_setup(request):
    """Exécute les migrations et collectstatic."""
    secret = request.GET.get('key', '')
    if secret != 'lmdsetup2026':
        return HttpResponse("Accès refusé.", status=403)

    import os
    from django.db import connection

    output = io.StringIO()
    results = []

    results.append("=" * 50)
    results.append("LMD Manager Pro - Setup cPanel")
    results.append("=" * 50)

    # 1. Désactiver les contrôles de clés étrangères
    results.append("\n[1/4] Désactivation des contrôles FK...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        results.append("✓ FK checks désactivés")
    except Exception as e:
        results.append(f"✗ Erreur FK: {e}")

    # 2. Migrations
    results.append("\n[2/4] Exécution des migrations...")
    try:
        call_command('migrate', verbosity=1, stdout=output)
        results.append(output.getvalue())
        results.append("✓ Migrations terminées avec succès!")
    except Exception as e:
        results.append(f"✗ Erreur: {e}")

    # Réactiver les FK
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        results.append("✓ FK checks réactivés")
    except Exception as e:
        results.append(f"✗ Erreur FK: {e}")

    # 3. Collectstatic
    output = io.StringIO()
    results.append("\n[3/4] Collecte des fichiers statiques...")
    try:
        # Créer le dossier staticfiles s'il n'existe pas
        static_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'staticfiles')
        os.makedirs(static_root, exist_ok=True)
        call_command('collectstatic', '--noinput', verbosity=1, stdout=output)
        results.append(output.getvalue()[:500])
        results.append("✓ Fichiers statiques collectés!")
    except Exception as e:
        results.append(f"✗ Erreur: {e}")

    # 4. Créer le superuser
    results.append("\n[4/5] Création du super utilisateur...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = 'admin'
        password = 'Admin@2026!'
        if User.objects.filter(username=username).exists():
            results.append(f"L'utilisateur '{username}' existe déjà.")
        else:
            user = User(
                username=username,
                email='admin@lmdmanagerpro.com',
                is_staff=True,
                is_superuser=True,
                is_active=True,
            )
            if hasattr(user, 'role'):
                user.role = 'ADMIN'
            user.set_password(password)
            user.save()
            results.append(f"✓ Super utilisateur '{username}' créé!")
            results.append(f"  Mot de passe: {password}")
            results.append("  ⚠ CHANGEZ ce mot de passe!")
    except Exception as e:
        results.append(f"✗ Erreur: {e}")

    # 5. Vérification
    results.append("\n[5/5] Vérification...")
    try:
        count = User.objects.count()
        results.append(f"✓ Base de données OK - {count} utilisateur(s)")

        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
        results.append(f"✓ {len(tables)} tables créées")
    except Exception as e:
        results.append(f"✗ Erreur: {e}")

    results.append("\n" + "=" * 50)
    results.append("Setup terminé!")

    return HttpResponse("\n".join(results), content_type="text/plain; charset=utf-8")


def create_admin(request):
    """Crée un super utilisateur."""
    secret = request.GET.get('key', '')
    if secret != 'lmdsetup2026':
        return HttpResponse("Accès refusé.", status=403)

    from django.contrib.auth import get_user_model
    User = get_user_model()

    username = 'admin'
    password = 'Admin@2026!'

    results = []
    if User.objects.filter(username=username).exists():
        results.append(f"L'utilisateur '{username}' existe déjà.")
    else:
        try:
            user = User.objects.create_superuser(
                username=username,
                email='admin@lmdmanagerpro.com',
                password=password,
            )
            results.append(f"✓ Super utilisateur '{username}' créé!")
            results.append(f"Mot de passe: {password}")
            results.append("⚠ CHANGEZ ce mot de passe après la première connexion!")
        except Exception as e:
            results.append(f"✗ Erreur: {e}")

    return HttpResponse("\n".join(results), content_type="text/plain; charset=utf-8")
