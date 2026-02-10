from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Etudiant, Enseignant, UE, EC, Jury, Evaluation, Inscription, Cohorte
from reglage.models import Departement, Section, Classe as ReglageClasse, AnneeAcademique as ReglageAnneeAcademique


class DepartementChoiceField(forms.ModelChoiceField):
    """ModelChoiceField affichant uniquement la désignation du département (reglage.Departement)."""
    def label_from_instance(self, obj):
        return obj.designation_departement


class PhotoForm(forms.Form):
    """Formulaire pour modifier uniquement la photo de profil"""
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control d-none',
            'id': 'photo-input-profil',
            'accept': 'image/*'
        })
    )


class UserForm(UserCreationForm):
    """Formulaire pour la création d'utilisateurs"""
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})


class UserEditForm(forms.ModelForm):
    """Formulaire pour la modification d'utilisateurs (sans mot de passe)"""
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class EtudiantForm(forms.ModelForm):
    """Formulaire pour la gestion des étudiants"""
    
    class Meta:
        model = Etudiant
        fields = ['matricule_et', 'nom_complet', 'sexe', 'date_naiss', 'nationalite', 'telephone', 'photo']
        widgets = {
            'matricule_et': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Matricule'
            }),
            'nom_complet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom complet'
            }),
            'sexe': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date_naiss': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'nationalite': forms.Select(attrs={
                'class': 'form-select'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Téléphone'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control d-none',
                'id': 'photo-input-etudiant',
                'accept': 'image/*'
            }),
        }


class EnseignantForm(forms.ModelForm):
    """Formulaire pour la gestion des enseignants"""
    
    code_dpt = DepartementChoiceField(
        queryset=Departement.objects.all(),
        required=False,
        label='',
        empty_label='Département',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_departement'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Libellés explicites pour les choix vides
        if hasattr(self.fields.get('fonction'), 'empty_label'):
            self.fields['fonction'].empty_label = 'Fonction'
        if hasattr(self.fields.get('grade'), 'empty_label'):
            self.fields['grade'].empty_label = 'Grade'
        if hasattr(self.fields.get('categorie'), 'empty_label'):
            self.fields['categorie'].empty_label = 'Catégorie'
        if hasattr(self.fields.get('code_dpt'), 'empty_label'):
            self.fields['code_dpt'].empty_label = 'Département'
        if hasattr(self.fields.get('code_section'), 'empty_label'):
            self.fields['code_section'].empty_label = 'Section'

    class Meta:
        model = Enseignant
        fields = ['matricule_en', 'nom_complet', 'telephone', 'fonction', 'grade', 'categorie', 'code_dpt', 'code_section', 'photo']
        widgets = {
            'matricule_en': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Matricule'
            }),
            'nom_complet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom complet'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Téléphone'
            }),
            'fonction': forms.Select(attrs={
                'class': 'form-select'
            }),
            'grade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-select'
            }),
            'code_section': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_section'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control d-none',
                'id': 'photo-input',
                'accept': 'image/*'
            }),
        }
        labels = {
            'matricule_en': '',
            'nom_complet': '',
            'telephone': '',
            'fonction': '',
            'grade': '',
            'categorie': '',
            'code_section': '',
            'photo': '',
        }


class UEForm(forms.ModelForm):
    """Formulaire pour la gestion des UE"""
    
    class Meta:
        model = UE
        fields = ['code_ue', 'intitule_ue', 'credit', 'semestre', 'seuil', 'categorie', 'classe']
        widgets = {
            'code_ue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: UE101'
            }),
            'intitule_ue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Programmation Python'
            }),
            'credit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Nombre de crédits'
            }),
            'semestre': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'placeholder': 'Numéro du semestre'
            }),
            'seuil': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'placeholder': 'Seuil'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-select'
            }),
            'classe': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class ECForm(forms.ModelForm):
    """Formulaire pour la gestion des EC"""
    
    CATEGORIE_CHOICES = [
        ('', '---------'),
        ('A', 'A'),
        ('B', 'B'),
    ]
    
    categorie = forms.ChoiceField(
        choices=CATEGORIE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = EC
        fields = ['code_ec', 'intitule_ue', 'credit', 'code_ue', 'seuil', 'categorie', 'classe']
        widgets = {
            'code_ec': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: EC101'
            }),
            'intitule_ue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Introduction à Python'
            }),
            'credit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Nombre de crédits'
            }),
            'code_ue': forms.Select(attrs={
                'class': 'form-select'
            }),
            'seuil': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'placeholder': 'Seuil'
            }),
            'classe': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class JuryForm(forms.ModelForm):
    """Formulaire pour la gestion des jurys"""
    
    president = forms.ModelChoiceField(
        queryset=Enseignant.objects.all().order_by('nom_complet'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label=''
    )
    secretaire = forms.ModelChoiceField(
        queryset=Enseignant.objects.all().order_by('nom_complet'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label=''
    )
    membre = forms.ModelChoiceField(
        queryset=Enseignant.objects.all().order_by('nom_complet'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label=''
    )
    
    class Meta:
        model = Jury
        fields = ['code_jury', 'code_classe', 'annee_academique', 'president', 'secretaire', 'membre', 'decision']
        labels = {
            'code_jury': '',
            'code_classe': '',
            'annee_academique': '',
            'decision': '',
        }
        widgets = {
            'code_jury': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code du jury (ex: JURY-L1-2024)'
            }),
            'code_classe': forms.Select(attrs={
                'class': 'form-select'
            }),
            'annee_academique': forms.Select(attrs={
                'class': 'form-select'
            }),
            'decision': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Décision DG (ex: DG 005/2025 du Février 2025)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter les placeholders pour les selects
        self.fields['president'].empty_label = "-- Sélectionner le président --"
        self.fields['secretaire'].empty_label = "-- Sélectionner le secrétaire --"
        self.fields['membre'].empty_label = "-- Sélectionner un membre (optionnel) --"
        self.fields['code_classe'].empty_label = "-- Sélectionner la classe --"
        
        # Charger les années académiques disponibles
        from reglage.models import AnneeAcademique
        annees = AnneeAcademique.objects.all().order_by('-code_anac')
        choices = [('', '-- Sélectionner l\'année académique --')]
        choices += [(a.code_anac, a.designation_anac) for a in annees]
        self.fields['annee_academique'] = forms.ChoiceField(
            choices=choices,
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=False,
            label=''
        )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Stocker le matricule de l'enseignant au lieu de l'objet
        if self.cleaned_data.get('president'):
            instance.president = self.cleaned_data['president'].matricule_en
        if self.cleaned_data.get('secretaire'):
            instance.secretaire = self.cleaned_data['secretaire'].matricule_en
        if self.cleaned_data.get('membre'):
            instance.membre = self.cleaned_data['membre'].matricule_en
        if commit:
            instance.save()
        return instance


class EvaluationForm(forms.ModelForm):
    """Formulaire pour la gestion des évaluations"""
    
    class Meta:
        model = Evaluation
        fields = ['matricule_etudiant', 'code_ue', 'code_ec', 'cc', 'examen', 'rattrapage', 'rachat']
        widgets = {
            'matricule_etudiant': forms.Select(attrs={
                'class': 'form-select'
            }),
            'code_ue': forms.Select(attrs={
                'class': 'form-select'
            }),
            'code_ec': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cc': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '20',
                'step': '0.01',
                'placeholder': 'Note CC (/20)'
            }),
            'examen': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '20',
                'step': '0.01',
                'placeholder': 'Note Examen (/20)'
            }),
            'rattrapage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '20',
                'step': '0.01',
                'placeholder': 'Note Rattrapage (/20) - Optionnel'
            }),
            'rachat': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '20',
                'step': '0.01',
                'placeholder': 'Note Rachat (/20) - Optionnel'
            }),
        }


class AttributionForm(forms.ModelForm):
    """Formulaire pour les attributions"""
    
    code_cours = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=''
    )
    
    class Meta:
        from .models import Attribution
        model = Attribution
        fields = ['code_attribution', 'matricule_en', 'code_cours', 'type_charge', 'annee_academique']
        widgets = {
            'code_attribution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code Attribution (auto-généré si vide)'
            }),
            'matricule_en': forms.Select(attrs={
                'class': 'form-select'
            }),
            'type_charge': forms.Select(attrs={
                'class': 'form-select'
            }),
            'annee_academique': forms.HiddenInput(),
        }
        labels = {
            'code_attribution': '',
            'matricule_en': '',
            'type_charge': '',
            'annee_academique': '',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import CoursAttribution
        
        # Peupler les choix de code_cours depuis CoursAttribution
        cours_choices = [('', '-- Sélectionner Cours --')]
        for cours in CoursAttribution.objects.all().order_by('type_cours', 'code_cours'):
            label = f"{cours.code_cours} - {cours.intitule} ({cours.type_cours})"
            cours_choices.append((cours.code_cours, label))
        self.fields['code_cours'].choices = cours_choices
        
        if hasattr(self.fields.get('matricule_en'), 'empty_label'):
            self.fields['matricule_en'].empty_label = '-- Sélectionner Enseignant --'
        if hasattr(self.fields.get('type_charge'), 'empty_label'):
            self.fields['type_charge'].empty_label = '-- Type Charge --'


class CohorteForm(forms.ModelForm):
    """Formulaire pour la gestion des cohortes"""
    
    class Meta:
        model = Cohorte
        fields = ['code_cohorte', 'lib_cohorte', 'debut']
        widgets = {
            'code_cohorte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: COH2024'
            }),
            'lib_cohorte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Cohorte 2024-2025'
            }),
            'debut': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class InscriptionForm(forms.ModelForm):
    """Formulaire pour la gestion des inscriptions"""
    
    matricule_etudiant = forms.ModelChoiceField(
        queryset=Etudiant.objects.all().order_by('nom_complet'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        to_field_name='matricule_et'
    )
    
    annee_academique = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    code_classe = forms.ModelChoiceField(
        queryset=ReglageClasse.objects.all().order_by('code_classe'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        to_field_name='code_classe'
    )
    
    cohorte = forms.ModelChoiceField(
        queryset=Cohorte.objects.all().order_by('code_cohorte'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        to_field_name='code_cohorte',
        required=False
    )
    
    class Meta:
        model = Inscription
        fields = ['code_inscription', 'matricule_etudiant', 'annee_academique', 'code_classe', 'cohorte']
        widgets = {
            'code_inscription': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: INS2024001'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populer le combo année académique depuis reglage
        annees = ReglageAnneeAcademique.objects.all().order_by('-code_anac')
        self.fields['annee_academique'].choices = [('', "-- Sélectionner l'année --")] + [
            (a.code_anac, f"{a.code_anac} - {a.designation_anac}") for a in annees
        ]
        
        # Ajouter les labels vides pour les selects
        self.fields['matricule_etudiant'].empty_label = "-- Sélectionner l'étudiant --"
        self.fields['code_classe'].empty_label = '-- Sélectionner la classe --'
        self.fields['cohorte'].empty_label = '-- Sélectionner la cohorte (optionnel) --'
