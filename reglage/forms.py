from django import forms
from .models import (
    Section, Departement, Mention, Niveau, Semestre, 
    Classe, AnneeAcademique, Grade, Fonction, TypeCharge, Categorie
)


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['code_section', 'designation_section']
        widgets = {
            'code_section': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: SEC001'}),
            'designation_section': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Désignation'}),
        }


class DepartementForm(forms.ModelForm):
    class Meta:
        model = Departement
        fields = ['code_departement', 'designation_departement', 'code_section']
        widgets = {
            'code_departement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: DPT001'}),
            'designation_departement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Désignation'}),
            'code_section': forms.Select(attrs={'class': 'form-select'}),
        }


class MentionForm(forms.ModelForm):
    class Meta:
        model = Mention
        fields = ['code_mention', 'designation_mention']
        widgets = {
            'code_mention': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: MEN001'}),
            'designation_mention': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Désignation'}),
        }


class NiveauForm(forms.ModelForm):
    class Meta:
        model = Niveau
        fields = ['code_niveau', 'designation_niveau']
        widgets = {
            'code_niveau': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: L1, L2, M1'}),
            'designation_niveau': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Désignation'}),
        }


class SemestreForm(forms.ModelForm):
    class Meta:
        model = Semestre
        fields = ['code_semestre', 'designation_semestre']
        widgets = {
            'code_semestre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: S1, S2'}),
            'designation_semestre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Désignation'}),
        }


class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ['code_niveau', 'code_mention']
        widgets = {
            'code_niveau': forms.Select(attrs={'class': 'form-select'}),
            'code_mention': forms.Select(attrs={'class': 'form-select'}),
        }


class AnneeAcademiqueForm(forms.ModelForm):
    class Meta:
        model = AnneeAcademique
        fields = ['code_anac', 'designation_anac', 'date_debut', 'date_fin', 'active']
        widgets = {
            'code_anac': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2024-2025'}),
            'designation_anac': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Désignation'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['code_grade', 'designation_grade']
        widgets = {
            'code_grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: PROF, CT'}),
            'designation_grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Désignation'}),
        }


class FonctionForm(forms.ModelForm):
    class Meta:
        model = Fonction
        fields = ['code_fonction', 'designation_fonction']
        widgets = {
            'code_fonction': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ENS, ADMIN'}),
            'designation_fonction': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Désignation'}),
        }


class TypeChargeForm(forms.ModelForm):
    class Meta:
        model = TypeCharge
        fields = ['code_type', 'designation_typecharge']
        widgets = {
            'code_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: CM, TD, TP'}),
            'designation_typecharge': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Désignation'}),
        }


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['code_categorie', 'designation_categorie']
        widgets = {
            'code_categorie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: CAT001'}),
            'designation_categorie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Désignation'}),
        }
