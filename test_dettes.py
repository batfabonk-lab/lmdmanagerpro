import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
User = get_user_model()

c = Client()
user = User.objects.filter(is_staff=True).first()
if not user:
    print("Pas d'utilisateur staff")
    exit()

c.force_login(user)

# Test profil
resp1 = c.get('/gestion/etudiants/voir/ETU006/')
print(f"Profil: status={resp1.status_code}")
if resp1.status_code == 200:
    content = resp1.content.decode()
    print(f"  Section Dettes: {'TROUVEE' if 'Dettes' in content else 'ABSENTE'}")
    print(f"  Mot Validees: {'TROUVÉ' if 'Valid' in content else 'ABSENT'}")
    ctx = resp1.context
    if ctx:
        print(f"  nb_total_dettes = {ctx.get('nb_total_dettes', 'N/A')}")
        print(f"  nb_dettes_compensees = {ctx.get('nb_dettes_compensees', 'N/A')}")
        print(f"  nb_dettes_liquidees = {ctx.get('nb_dettes_liquidees', 'N/A')}")
elif resp1.status_code in (301, 302):
    print(f"  Redirect: {resp1.url}")

# Test suivi dettes
resp2 = c.get('/gestion/etudiants/suivi-dettes/ETU006/')
print(f"\nSuivi dettes: status={resp2.status_code}")
if resp2.status_code == 200:
    content2 = resp2.content.decode()
    print(f"  Mot Validee: {'TROUVÉ' if 'Valid' in content2 else 'ABSENT'}")
    print(f"  Mot Liquidee: {'ENCORE PRESENT!' if 'Liquid' in content2 else 'absent (ok)'}")
    ctx2 = resp2.context
    if ctx2:
        print(f"  nb_compensees = {ctx2.get('nb_compensees', 'N/A')}")
        print(f"  nb_liquidees = {ctx2.get('nb_liquidees', 'N/A')}")
elif resp2.status_code in (301, 302):
    print(f"  Redirect: {resp2.url}")
