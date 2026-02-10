from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pandas as pd
from .models import (
    Section, Departement, Mention, Niveau, Semestre,
    Classe, AnneeAcademique, Grade, Fonction, TypeCharge, Categorie
)
from .forms import (
    SectionForm, DepartementForm, MentionForm, NiveauForm, SemestreForm,
    ClasseForm, AnneeAcademiqueForm, GradeForm, FonctionForm, TypeChargeForm, CategorieForm
)


# ========== SECTIONS ==========
@login_required
def gestion_sections(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    sections = Section.objects.all()
    form = SectionForm()
    
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section ajoutée avec succès!')
            return redirect('gestion_sections')
    
    return render(request, 'reglage/sections.html', {'items': sections, 'form': form})


@login_required
def modifier_section(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Section, code_section=code)
    form = SectionForm(request.POST or None, instance=item)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Section modifiée avec succès!')
        return redirect('gestion_sections')
    
    return render(request, 'reglage/modifier.html', {'item': item, 'form': form, 'titre': 'Section', 'retour': 'gestion_sections'})


@login_required
def supprimer_section(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Section, code_section=code)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Section supprimée avec succès!')
        return redirect('gestion_sections')
    
    return render(request, 'reglage/supprimer.html', {'item': item, 'titre': 'Section', 'retour': 'gestion_sections'})


# ========== DEPARTEMENTS ==========
@login_required
def gestion_departements(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    departements = Departement.objects.all().select_related('code_section')
    form = DepartementForm()
    
    if request.method == 'POST':
        form = DepartementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Département ajouté avec succès!')
            return redirect('gestion_departements')
    
    return render(request, 'reglage/departements.html', {'items': departements, 'form': form})


@login_required
def modifier_departement(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Departement, code_departement=code)
    form = DepartementForm(request.POST or None, instance=item)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Département modifié avec succès!')
        return redirect('gestion_departements')
    
    return render(request, 'reglage/modifier.html', {'item': item, 'form': form, 'titre': 'Département', 'retour': 'gestion_departements'})


@login_required
def supprimer_departement(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Departement, code_departement=code)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Département supprimé avec succès!')
        return redirect('gestion_departements')
    
    return render(request, 'reglage/supprimer.html', {'item': item, 'titre': 'Département', 'retour': 'gestion_departements'})


# ========== MENTIONS ==========
@login_required
def gestion_mentions(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    mentions = Mention.objects.all()
    form = MentionForm()
    
    if request.method == 'POST':
        form = MentionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mention ajoutée avec succès!')
            return redirect('gestion_mentions')
    
    return render(request, 'reglage/mentions.html', {'items': mentions, 'form': form})


@login_required
def modifier_mention(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Mention, code_mention=code)
    form = MentionForm(request.POST or None, instance=item)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Mention modifiée avec succès!')
        return redirect('gestion_mentions')
    
    return render(request, 'reglage/modifier.html', {'item': item, 'form': form, 'titre': 'Mention', 'retour': 'gestion_mentions'})


@login_required
def supprimer_mention(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Mention, code_mention=code)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Mention supprimée avec succès!')
        return redirect('gestion_mentions')
    
    return render(request, 'reglage/supprimer.html', {'item': item, 'titre': 'Mention', 'retour': 'gestion_mentions'})


@login_required
def generer_classes_pour_mentions(request):
    """Générer automatiquement des classes pour chaque mention avec tous les niveaux disponibles"""
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        messages.error(request, 'Accès non autorisé.')
        return redirect('gestion_mentions')
    
    if request.method == 'POST':
        mentions = Mention.objects.all()
        niveaux = Niveau.objects.all()
        classes_crees = 0
        classes_existantes = 0
        
        for mention in mentions:
            for niveau in niveaux:
                # Vérifier si la classe existe déjà
                code_classe = f"{niveau.code_niveau}{mention.code_mention}"
                
                try:
                    classe, created = Classe.objects.get_or_create(
                        code_classe=code_classe,
                        defaults={
                            'code_niveau': niveau,
                            'code_mention': mention,
                            'designation_classe': f"{niveau.designation_niveau} {mention.designation_mention}"
                        }
                    )
                    
                    if created:
                        classes_crees += 1
                    else:
                        classes_existantes += 1
                        
                except Exception as e:
                    messages.error(request, f'Erreur lors de la création de la classe {code_classe}: {str(e)}')
        
        if classes_crees > 0:
            messages.success(request, f'{classes_crees} classe(s) générée(s) avec succès!')
        if classes_existantes > 0:
            messages.info(request, f'{classes_existantes} classe(s) existaient déjà.')
        
        return redirect('gestion_mentions')
    
    # Pour une requête GET, rediriger vers la page des mentions
    return redirect('gestion_mentions')


# ========== NIVEAUX ==========
@login_required
def gestion_niveaux(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    niveaux = Niveau.objects.all()
    form = NiveauForm()
    
    if request.method == 'POST':
        form = NiveauForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Niveau ajouté avec succès!')
            return redirect('gestion_niveaux')
    
    return render(request, 'reglage/niveaux.html', {'items': niveaux, 'form': form})


@login_required
def modifier_niveau(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Niveau, code_niveau=code)
    form = NiveauForm(request.POST or None, instance=item)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Niveau modifié avec succès!')
        return redirect('gestion_niveaux')
    
    return render(request, 'reglage/modifier.html', {'item': item, 'form': form, 'titre': 'Niveau', 'retour': 'gestion_niveaux'})


@login_required
def supprimer_niveau(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Niveau, code_niveau=code)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Niveau supprimé avec succès!')
        return redirect('gestion_niveaux')
    
    return render(request, 'reglage/supprimer.html', {'item': item, 'titre': 'Niveau', 'retour': 'gestion_niveaux'})


# ========== SEMESTRES ==========
@login_required
def gestion_semestres(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    semestres = Semestre.objects.all()
    form = SemestreForm()
    
    if request.method == 'POST':
        form = SemestreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Semestre ajouté avec succès!')
            return redirect('gestion_semestres')
    
    return render(request, 'reglage/semestres.html', {'items': semestres, 'form': form})


@login_required
def modifier_semestre(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Semestre, code_semestre=code)
    form = SemestreForm(request.POST or None, instance=item)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Semestre modifié avec succès!')
        return redirect('gestion_semestres')
    
    return render(request, 'reglage/modifier.html', {'item': item, 'form': form, 'titre': 'Semestre', 'retour': 'gestion_semestres'})


@login_required
def supprimer_semestre(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Semestre, code_semestre=code)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Semestre supprimé avec succès!')
        return redirect('gestion_semestres')
    
    return render(request, 'reglage/supprimer.html', {'item': item, 'titre': 'Semestre', 'retour': 'gestion_semestres'})


# ========== CLASSES ==========
@login_required
def gestion_classes(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    classes = Classe.objects.all().select_related('code_niveau', 'code_mention')
    form = ClasseForm()
    
    if request.method == 'POST':
        form = ClasseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Classe ajoutée avec succès!')
            return redirect('gestion_classes')
    
    return render(request, 'reglage/classes.html', {'items': classes, 'form': form})


@login_required
def modifier_classe(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Classe, code_classe=code)
    form = ClasseForm(request.POST or None, instance=item)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Classe modifiée avec succès!')
        return redirect('gestion_classes')
    
    return render(request, 'reglage/modifier.html', {'item': item, 'form': form, 'titre': 'Classe', 'retour': 'gestion_classes'})


@login_required
def supprimer_classe(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Classe, code_classe=code)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Classe supprimée avec succès!')
        return redirect('gestion_classes')
    
    return render(request, 'reglage/supprimer.html', {'item': item, 'titre': 'Classe', 'retour': 'gestion_classes'})


# ========== ANNEES ACADEMIQUES ==========
@login_required
def gestion_annees(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    annees = AnneeAcademique.objects.all()
    form = AnneeAcademiqueForm()
    
    if request.method == 'POST':
        form = AnneeAcademiqueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Année académique ajoutée avec succès!')
            return redirect('gestion_annees')
    
    return render(request, 'reglage/annees.html', {'items': annees, 'form': form})


@login_required
def modifier_annee(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(AnneeAcademique, code_anac=code)
    form = AnneeAcademiqueForm(request.POST or None, instance=item)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Année académique modifiée avec succès!')
        return redirect('gestion_annees')
    
    return render(request, 'reglage/modifier.html', {'item': item, 'form': form, 'titre': 'Année Académique', 'retour': 'gestion_annees'})


@login_required
def supprimer_annee(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(AnneeAcademique, code_anac=code)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Année académique supprimée avec succès!')
        return redirect('gestion_annees')
    
    return render(request, 'reglage/supprimer.html', {'item': item, 'titre': 'Année Académique', 'retour': 'gestion_annees'})


@login_required
def activer_annee(request, code):
    """Définir une année académique comme année en cours"""
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    annee = get_object_or_404(AnneeAcademique, code_anac=code)
    annee.active = True
    annee.save()
    messages.success(request, f'L\'année {annee.designation_anac} est maintenant l\'année en cours!')
    return redirect('gestion_annees')


# ========== GRADES ==========
@login_required
def gestion_grades(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    grades = Grade.objects.all()
    form = GradeForm()
    
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade ajouté avec succès!')
            return redirect('gestion_grades')
    
    return render(request, 'reglage/grades.html', {'items': grades, 'form': form})


@login_required
def modifier_grade(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Grade, code_grade=code)
    form = GradeForm(request.POST or None, instance=item)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Grade modifié avec succès!')
        return redirect('gestion_grades')
    
    return render(request, 'reglage/modifier.html', {'item': item, 'form': form, 'titre': 'Grade', 'retour': 'gestion_grades'})


@login_required
def supprimer_grade(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Grade, code_grade=code)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Grade supprimé avec succès!')
    return render(request, 'reglage/supprimer.html', {'item': item, 'titre': 'Grade', 'retour': 'gestion_grades'})


# ========== FONCTIONS ========== 
@login_required
def gestion_fonctions(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    fonctions = Fonction.objects.all()
    form = FonctionForm()
    
    if request.method == 'POST':
        form = FonctionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fonction ajoutée avec succès!')
            return redirect('gestion_fonctions')
    
    return render(request, 'reglage/fonctions.html', {'items': fonctions, 'form': form})


@login_required
def import_fonctions(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        try:
            df = pd.read_excel(excel_file)
            success_count = 0
            error_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    code = str(row['code_fonction']).strip()
                    designation = str(row['designation_fonction']).strip()

                    Fonction.objects.update_or_create(
                        code_fonction=code,
                        defaults={
                            'designation_fonction': designation,
                        }
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"Ligne {index + 2}: {str(e)}")

            if success_count > 0:
                messages.success(request, f'{success_count} fonction(s) importée(s) avec succès!')
            if error_count > 0:
                messages.warning(request, f'{error_count} erreur(s) lors de l\'importation.')
                for error in errors[:5]:
                    messages.error(request, error)

        except Exception as e:
            messages.error(request, f'Erreur lors de la lecture du fichier: {str(e)}')

        return redirect('gestion_fonctions')

    return render(request, 'gestion/import_excel.html', {
        'titre': 'Fonctions',
        'colonnes': ['code_fonction', 'designation_fonction'],
        'retour': 'gestion_fonctions'
    })


@login_required
def modifier_fonction(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Fonction, code_fonction=code)
    form = FonctionForm(request.POST or None, instance=item)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Fonction modifiée avec succès!')
        return redirect('gestion_fonctions')
    
    return render(request, 'reglage/modifier.html', {'item': item, 'form': form, 'titre': 'Fonction', 'retour': 'gestion_fonctions'})


@login_required
def supprimer_fonction(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Fonction, code_fonction=code)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Fonction supprimée avec succès!')
        return redirect('gestion_fonctions')
    
    return render(request, 'reglage/supprimer.html', {'item': item, 'titre': 'Fonction', 'retour': 'gestion_fonctions'})


# ========== TYPES DE CHARGE ==========
@login_required
def gestion_typecharges(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    typecharges = TypeCharge.objects.all()
    form = TypeChargeForm()
    
    if request.method == 'POST':
        form = TypeChargeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Type de charge ajouté avec succès!')
            return redirect('gestion_typecharges')
    
    return render(request, 'reglage/typecharges.html', {'items': typecharges, 'form': form})


@login_required
def modifier_typecharge(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(TypeCharge, code_type=code)
    form = TypeChargeForm(request.POST or None, instance=item)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Type de charge modifié avec succès!')
        return redirect('gestion_typecharges')
    
    return render(request, 'reglage/modifier.html', {'item': item, 'form': form, 'titre': 'Type de Charge', 'retour': 'gestion_typecharges'})


@login_required
def supprimer_typecharge(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(TypeCharge, code_type=code)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Type de charge supprimé avec succès!')
        return redirect('gestion_typecharges')
    
    return render(request, 'reglage/supprimer.html', {'item': item, 'titre': 'Type de Charge', 'retour': 'gestion_typecharges'})


# ========== CATEGORIES ==========
@login_required
def gestion_categories(request):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    categories = Categorie.objects.all()
    form = CategorieForm()
    
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie ajoutée avec succès!')
            return redirect('gestion_categories')
    
    return render(request, 'reglage/categories.html', {'items': categories, 'form': form})


@login_required
def modifier_categorie(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Categorie, code_categorie=code)
    form = CategorieForm(request.POST or None, instance=item)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Catégorie modifiée avec succès!')
        return redirect('gestion_categories')
    
    return render(request, 'reglage/modifier.html', {'item': item, 'form': form, 'titre': 'Catégorie', 'retour': 'gestion_categories'})


@login_required
def supprimer_categorie(request, code):
    if not (request.user.is_staff or request.user.role == 'GESTIONNAIRE'):
        return redirect('home')
    
    item = get_object_or_404(Categorie, code_categorie=code)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Catégorie supprimée avec succès!')
        return redirect('gestion_categories')
    
    return render(request, 'reglage/supprimer.html', {'item': item, 'titre': 'Catégorie', 'retour': 'gestion_categories'})
