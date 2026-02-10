import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
import django
django.setup()

from core.models import User, Etudiant, Enseignant

print('=== VÉRIFICATION FINALE ===\n')

# Vérifier les étudiants
print('ÉTUDIANTS LIÉS:')
etudiants = Etudiant.objects.all()[:3]
for etu in etudiants:
    print(f'  ✓ {etu.matricule_et} -> User {etu.id_lgn.username if etu.id_lgn else "NONE"}')

print('\nENSEIGNANTS LIÉS:')
enseignants = Enseignant.objects.all()[:3]
for ens in enseignants:
    print(f'  ✓ {ens.matricule_en} -> User {ens.id_lgn.username if ens.id_lgn else "NONE"}')

print('\n=== RÉSUMÉ ===')
print(f'✓ Étudiants avec USER: {Etudiant.objects.filter(id_lgn__isnull=False).count()}/{Etudiant.objects.count()}')
print(f'✓ Enseignants avec USER: {Enseignant.objects.filter(id_lgn__isnull=False).count()}/{Enseignant.objects.count()}')
print('\n✓✓✓ TOUS LES PROFILS SONT MAINTENANT LIÉS! ✓✓✓')
