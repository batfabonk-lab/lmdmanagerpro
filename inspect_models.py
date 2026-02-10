#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmdmanagersystem.settings')
django.setup()

from reglage.models import Section, Departement, AnneeAcademique
from core.models import Enseignant, Etudiant

print("Section fields:", [f.name for f in Section._meta.fields])
print("Departement fields:", [f.name for f in Departement._meta.fields])
print("AnneeAcademique fields:", [f.name for f in AnneeAcademique._meta.fields])
print("Enseignant fields:", [f.name for f in Enseignant._meta.fields])
print("Etudiant fields:", [f.name for f in Etudiant._meta.fields])
