"""Vue temporaire pour setup d'une institution (migrations + superuser).
Accès: /slug-institution/setup-migrate/?key=lmdsetup2026
Le middleware route automatiquement vers la bonne BD via le slug URL.
SUPPRIMER LES URLS DE SETUP après le déploiement!"""
import io
import os
from django.http import HttpResponse
from django.core.management import call_command
from django.conf import settings as django_settings
from django.db import connections


def run_setup(request):
    """Migrations + collectstatic + superuser pour l'institution courante."""
    secret = request.GET.get('key', '')
    if secret != 'lmdsetup2026':
        return HttpResponse("Accès refusé.", status=403)

    # Déterminer la BD à utiliser via le middleware d'institution
    db_alias = getattr(request, 'institution_slug', None)
    institutions = getattr(django_settings, 'INSTITUTIONS', {})
    if db_alias and db_alias in institutions:
        db_alias = institutions[db_alias].get('database', db_alias)
    else:
        db_alias = 'default'

    db_config = django_settings.DATABASES.get(db_alias, {})
    inst_name = getattr(request, 'institution_name', db_alias)

    results = []
    results.append("=" * 50)
    results.append(f"Setup: {inst_name}")
    results.append(f"Database: {db_alias} ({db_config.get('NAME', '?')})")
    results.append("=" * 50)

    connection = connections[db_alias]

    # 1. Désactiver FK checks
    results.append("\n[1/4] Désactivation FK checks...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        results.append("OK")
    except Exception as e:
        results.append(f"Erreur: {e}")

    # 2. Migrations
    output = io.StringIO()
    results.append("\n[2/4] Migrations...")
    try:
        call_command('migrate', database=db_alias, verbosity=1, stdout=output)
        results.append(output.getvalue())
        results.append("OK - Migrations terminées")
    except Exception as e:
        results.append(f"Erreur: {e}")

    # Réactiver FK
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    except Exception:
        pass

    # 3. Collectstatic
    output = io.StringIO()
    results.append("\n[3/4] Collectstatic...")
    try:
        static_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'staticfiles')
        os.makedirs(static_root, exist_ok=True)
        call_command('collectstatic', '--noinput', verbosity=0, stdout=output)
        results.append("OK")
    except Exception as e:
        results.append(f"Erreur: {e}")

    # 4. Superuser
    results.append("\n[4/4] Création superuser...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = 'admin'
        password = 'Admin@2026!'
        if User.objects.using(db_alias).filter(username=username).exists():
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
            user.save(using=db_alias)
            results.append(f"Superuser '{username}' créé (mdp: {password})")
            results.append("CHANGEZ ce mot de passe!")
    except Exception as e:
        results.append(f"Erreur: {e}")

    # Vérification
    results.append("\n--- Vérification ---")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
        results.append(f"{len(tables)} tables créées")
    except Exception as e:
        results.append(f"Erreur: {e}")

    results.append("\n" + "=" * 50)
    results.append("Setup terminé!")

    return HttpResponse("\n".join(results), content_type="text/plain; charset=utf-8")
