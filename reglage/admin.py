from django.contrib import admin
from .models import (
    Section, Departement, Mention, Niveau, Semestre, Classe, AnneeAcademique,
    Grade, Fonction, TypeCharge, Categorie
)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['code_section', 'designation_section']
    search_fields = ['code_section', 'designation_section']
    list_per_page = 20


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ['code_departement', 'designation_departement', 'code_section']
    list_filter = ['code_section']
    search_fields = ['code_departement', 'designation_departement']
    list_per_page = 20


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ['code_mention', 'designation_mention']
    search_fields = ['code_mention', 'designation_mention']
    list_per_page = 20


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ['code_niveau', 'designation_niveau']
    search_fields = ['code_niveau', 'designation_niveau']
    list_per_page = 20


@admin.register(Semestre)
class SemestreAdmin(admin.ModelAdmin):
    list_display = ['code_semestre', 'designation_semestre']
    search_fields = ['code_semestre', 'designation_semestre']
    list_per_page = 20


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ['code_classe', 'designation_classe']
    search_fields = ['code_classe', 'designation_classe']
    list_per_page = 20


@admin.register(AnneeAcademique)
class AnneeAcademiqueAdmin(admin.ModelAdmin):
    list_display = ['code_anac', 'designation_anac', 'date_debut', 'date_fin', 'active']
    list_filter = ['active']
    search_fields = ['code_anac', 'designation_anac']
    list_editable = ['active']
    list_per_page = 20
    fieldsets = (
        ('Informations de base', {
            'fields': ('code_anac', 'designation_anac')
        }),
        ('Période', {
            'fields': ('date_debut', 'date_fin')
        }),
        ('Statut', {
            'fields': ('active',)
        }),
    )


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['code_grade', 'designation_grade']
    search_fields = ['code_grade', 'designation_grade']
    list_per_page = 20


@admin.register(Fonction)
class FonctionAdmin(admin.ModelAdmin):
    list_display = ['code_fonction', 'designation_fonction']
    search_fields = ['code_fonction', 'designation_fonction']
    list_per_page = 20


@admin.register(TypeCharge)
class TypeChargeAdmin(admin.ModelAdmin):
    list_display = ['code_type', 'designation_typecharge']
    search_fields = ['code_type', 'designation_typecharge']
    list_per_page = 20


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['code_categorie', 'designation_categorie']
    search_fields = ['code_categorie', 'designation_categorie']
    list_per_page = 20
