from django.urls import path
from . import views

urlpatterns = [
    # Sections
    path('sections/', views.gestion_sections, name='gestion_sections'),
    path('sections/modifier/<str:code>/', views.modifier_section, name='modifier_section'),
    path('sections/supprimer/<str:code>/', views.supprimer_section, name='supprimer_section'),
    
    # Départements
    path('departements/', views.gestion_departements, name='gestion_departements'),
    path('departements/modifier/<str:code>/', views.modifier_departement, name='modifier_departement'),
    path('departements/supprimer/<str:code>/', views.supprimer_departement, name='supprimer_departement'),
    
    # Mentions
    path('mentions/', views.gestion_mentions, name='gestion_mentions'),
    path('mentions/modifier/<str:code>/', views.modifier_mention, name='modifier_mention'),
    path('mentions/supprimer/<str:code>/', views.supprimer_mention, name='supprimer_mention'),
    path('mentions/generer-classes/', views.generer_classes_pour_mentions, name='generer_classes_pour_mentions'),
    
    # Niveaux
    path('niveaux/', views.gestion_niveaux, name='gestion_niveaux'),
    path('niveaux/modifier/<str:code>/', views.modifier_niveau, name='modifier_niveau'),
    path('niveaux/supprimer/<str:code>/', views.supprimer_niveau, name='supprimer_niveau'),
    
    # Semestres
    path('semestres/', views.gestion_semestres, name='gestion_semestres'),
    path('semestres/modifier/<str:code>/', views.modifier_semestre, name='modifier_semestre'),
    path('semestres/supprimer/<str:code>/', views.supprimer_semestre, name='supprimer_semestre'),
    
    # Classes
    path('classes/', views.gestion_classes, name='gestion_classes'),
    path('classes/modifier/<str:code>/', views.modifier_classe, name='modifier_classe_reglage'),
    path('classes/supprimer/<str:code>/', views.supprimer_classe, name='supprimer_classe_reglage'),
    
    # Années Académiques
    path('annees/', views.gestion_annees, name='gestion_annees'),
    path('annees/modifier/<str:code>/', views.modifier_annee, name='modifier_annee'),
    path('annees/supprimer/<str:code>/', views.supprimer_annee, name='supprimer_annee'),
    path('annees/activer/<str:code>/', views.activer_annee, name='activer_annee'),
    
    # Grades
    path('grades/', views.gestion_grades, name='gestion_grades'),
    path('grades/modifier/<str:code>/', views.modifier_grade, name='modifier_grade'),
    path('grades/supprimer/<str:code>/', views.supprimer_grade, name='supprimer_grade'),
    
    # Fonctions
    path('fonctions/', views.gestion_fonctions, name='gestion_fonctions'),
    path('fonctions/import/', views.import_fonctions, name='import_fonctions'),
    path('fonctions/modifier/<str:code>/', views.modifier_fonction, name='modifier_fonction'),
    path('fonctions/supprimer/<str:code>/', views.supprimer_fonction, name='supprimer_fonction'),
    
    # Types de Charge
    path('typecharges/', views.gestion_typecharges, name='gestion_typecharges'),
    path('typecharges/modifier/<str:code>/', views.modifier_typecharge, name='modifier_typecharge'),
    path('typecharges/supprimer/<str:code>/', views.supprimer_typecharge, name='supprimer_typecharge'),
    
    # Catégories
    path('categories/', views.gestion_categories, name='gestion_categories'),
    path('categories/modifier/<str:code>/', views.modifier_categorie, name='modifier_categorie'),
    path('categories/supprimer/<str:code>/', views.supprimer_categorie, name='supprimer_categorie'),
]
