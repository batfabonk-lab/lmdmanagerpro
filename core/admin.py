from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Section, Departement, UE, EC, Cohorte, 
    Etudiant, Enseignant, Classe, Inscription, Jury, Evaluation, Attribution,
    CommuniqueDeliberation, CommentaireCours, EvaluationEnseignement, Deliberation,
    DocumentCours
)

# Personnalisation du site d'administration
admin.site.site_header = "Administration Système LMD"
admin.site.site_title = "LMD Admin"
admin.site.index_title = "Gestion du Système Universitaire LMD"


# Configuration de l'admin User
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {'fields': ('role',)}),
    )


@admin.register(CommuniqueDeliberation)
class CommuniqueDeliberationAdmin(admin.ModelAdmin):
    list_display = ['code_classe', 'annee_academique', 'date_deliberation', 'date_creation']
    list_filter = ['annee_academique', 'code_classe']
    search_fields = ['annee_academique', 'contenu']
    list_per_page = 25


@admin.register(CommentaireCours)
class CommentaireCoursAdmin(admin.ModelAdmin):
    list_display = ['etudiant', 'annee_academique', 'type_cours', 'code_cours', 'date_creation']
    list_filter = ['annee_academique', 'type_cours']
    search_fields = ['code_cours', 'contenu', 'etudiant__matricule_et', 'etudiant__nom_complet']
    list_per_page = 25


@admin.register(EvaluationEnseignement)
class EvaluationEnseignementAdmin(admin.ModelAdmin):
    list_display = [
        'etudiant',
        'attribution',
        'annee_academique',
        'ponctualite',
        'maitrise_communication',
        'pedagogie_methodologie',
        'utilisation_tic',
        'disponibilite',
        'date_creation',
    ]
    list_filter = ['annee_academique', 'date_creation']
    search_fields = [
        'commentaire',
        'etudiant__matricule_et',
        'etudiant__nom_complet',
        'attribution__code_cours',
        'attribution__matricule_en__matricule_en',
        'attribution__matricule_en__nom_complet',
    ]
    list_per_page = 25


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['code_section', 'designation_sc']
    search_fields = ['code_section', 'designation_sc']


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ['code_dpt', 'designation_dpt', 'code_section']
    list_filter = ['code_section']
    search_fields = ['code_dpt', 'designation_dpt']


@admin.register(UE)
class UEAdmin(admin.ModelAdmin):
    list_display = ['code_ue', 'intitule_ue', 'credit', 'semestre', 'seuil', 'categorie', 'classe']
    list_filter = ['semestre', 'categorie', 'classe']
    search_fields = ['code_ue', 'intitule_ue']
    list_per_page = 25
    
    fieldsets = (
        ('Informations de Base', {
            'fields': ('code_ue', 'intitule_ue')
        }),
        ('Détails Académiques', {
            'fields': ('credit', 'semestre', 'seuil', 'categorie', 'classe')
        }),
    )
    
    actions = ['dupliquer_ue']
    
    def dupliquer_ue(self, request, queryset):
        """Action pour dupliquer des UE"""
        count = 0
        for ue in queryset:
            ue.pk = None
            ue.code_ue = f"{ue.code_ue}_COPIE"
            ue.save()
            count += 1
        
        self.message_user(request, f"{count} UE(s) dupliquée(s) avec succès.")
    
    dupliquer_ue.short_description = "Dupliquer les UE sélectionnées"


@admin.register(EC)
class ECAdmin(admin.ModelAdmin):
    list_display = ['code_ec', 'intitule_ue', 'credit', 'code_ue', 'seuil', 'categorie', 'classe']
    list_filter = ['code_ue', 'categorie', 'classe']
    search_fields = ['code_ec', 'intitule_ue']
    list_per_page = 25
    
    fieldsets = (
        ('Informations de Base', {
            'fields': ('code_ec', 'intitule_ue', 'code_ue')
        }),
        ('Détails Académiques', {
            'fields': ('credit', 'seuil', 'categorie', 'classe')
        }),
    )
    
    actions = ['exporter_liste_ec']
    
    def exporter_liste_ec(self, request, queryset):
        """Action pour exporter la liste des EC"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="elements_constitutifs.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Code EC', 'Intitulé', 'UE', 'Crédits', 'CMI', 'TP/TD'])
        
        for ec in queryset:
            writer.writerow([
                ec.code_ec,
                ec.intitule_ue,
                ec.code_ue,
                ec.credit,
                ec.cmi,
                ec.tp_td
            ])
        
        return response
    
    exporter_liste_ec.short_description = "Exporter les EC sélectionnés (CSV)"


@admin.register(Cohorte)
class CohorteAdmin(admin.ModelAdmin):
    list_display = ['code_cohorte', 'lib_cohorte', 'code_mention', 'debut']
    search_fields = ['code_cohorte', 'lib_cohorte']
    list_filter = ['code_mention']
    date_hierarchy = 'debut'


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ['matricule_et', 'nom_complet', 'sexe', 'telephone', 'nationalite']
    list_filter = ['sexe', 'nationalite']
    search_fields = ['matricule_et', 'nom_complet', 'telephone']
    date_hierarchy = 'date_naiss'
    list_per_page = 25
    
    fieldsets = (
        ('Informations Personnelles', {
            'fields': ('matricule_et', 'nom_complet', 'sexe', 'date_naiss', 'nationalite')
        }),
        ('Contact', {
            'fields': ('telephone', 'photo')
        }),
        ('Compte Utilisateur', {
            'fields': ('id_lgn',)
        }),
    )
    
    actions = ['exporter_liste_etudiants']
    
    def exporter_liste_etudiants(self, request, queryset):
        """Action pour exporter la liste des étudiants sélectionnés"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="etudiants.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Matricule', 'Nom Complet', 'Sexe', 'Date Naissance', 'Nationalité', 'Téléphone', 'Cohorte'])
        
        for etudiant in queryset:
            writer.writerow([
                etudiant.matricule_et,
                etudiant.nom_complet,
                etudiant.get_sexe_display(),
                etudiant.date_naiss,
                etudiant.nationalite,
                etudiant.telephone,
                etudiant.code_cohorte
            ])
        
        return response
    
    exporter_liste_etudiants.short_description = "Exporter les étudiants sélectionnés (CSV)"


@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ['matricule_en', 'nom_complet', 'telephone', 'grade', 'fonction', 'categorie', 'code_dpt']
    list_filter = ['grade', 'fonction', 'categorie', 'code_dpt']
    search_fields = ['matricule_en', 'nom_complet', 'telephone']
    list_per_page = 25
    
    fieldsets = (
        ('Informations Personnelles', {
            'fields': ('matricule_en', 'nom_complet', 'telephone', 'photo')
        }),
        ('Informations Professionnelles', {
            'fields': ('fonction', 'grade', 'categorie', 'code_dpt')
        }),
        ('Compte Utilisateur', {
            'fields': ('id_lgn',)
        }),
    )
    
    actions = ['exporter_liste_enseignants']
    
    def exporter_liste_enseignants(self, request, queryset):
        """Action pour exporter la liste des enseignants sélectionnés"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="enseignants.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Matricule', 'Nom Complet', 'Grade', 'Fonction', 'Département', 'Téléphone'])
        
        for enseignant in queryset:
            writer.writerow([
                enseignant.matricule_en,
                enseignant.nom_complet,
                enseignant.grade,
                enseignant.fonction,
                enseignant.code_dpt,
                enseignant.telephone
            ])
        
        return response
    
    exporter_liste_enseignants.short_description = "Exporter les enseignants sélectionnés (CSV)"


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ['code_classe', 'designation_cl']
    search_fields = ['code_classe', 'designation_cl']


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ['code_inscription', 'matricule_etudiant', 'annee_academique', 'code_classe', 'cohorte', 'decision_annuelle']
    list_filter = ['annee_academique', 'code_classe', 'decision_annuelle']
    search_fields = ['code_inscription', 'matricule_etudiant__nom_complet', 'annee_academique']


@admin.register(Jury)
class JuryAdmin(admin.ModelAdmin):
    list_display = ['code_jury', 'president', 'secretaire', 'membre', 'code_classe']
    list_filter = ['code_classe']
    search_fields = ['code_jury', 'president', 'secretaire', 'membre']
    list_per_page = 25
    
    fieldsets = (
        ('Informations du Jury', {
            'fields': ('code_jury', 'code_classe')
        }),
        ('Composition', {
            'fields': ('president', 'secretaire', 'membre')
        }),
        ('Décision', {
            'fields': ('decision',),
            'classes': ('collapse',)
        }),
        ('Compte Utilisateur', {
            'fields': ('id_lgn',)
        }),
    )
    
    actions = ['generer_rapport_jury']
    
    def generer_rapport_jury(self, request, queryset):
        """Action pour générer un rapport des jurys"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="jurys.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Code Jury', 'Classe', 'Président', 'Secrétaire', 'Membre', 'Décision'])
        
        for jury in queryset:
            writer.writerow([
                jury.code_jury,
                jury.code_classe,
                jury.president,
                jury.secretaire,
                jury.membre,
                jury.decision[:50] if jury.decision else ''
            ])
        
        return response
    
    generer_rapport_jury.short_description = "Exporter les jurys sélectionnés (CSV)"


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['id_ev', 'matricule_etudiant', 'code_ue', 'code_ec', 'cc', 'examen', 'statut']
    list_filter = ['statut', 'code_ue']
    search_fields = ['matricule_etudiant__nom_complet', 'code_ue__intitule_ue']
    readonly_fields = ['statut']
    
    def save_model(self, request, obj, form, change):
        """Override pour recalculer le statut lors de la sauvegarde"""
        super().save_model(request, obj, form, change)


@admin.register(Attribution)
class AttributionAdmin(admin.ModelAdmin):
    list_display = ['code_attribution', 'matricule_en', 'code_cours', 'get_type_cours', 'type_charge', 'annee_academique', 'date_attribution']
    list_filter = ['annee_academique', 'type_charge']
    search_fields = ['code_attribution', 'matricule_en__nom_complet', 'code_cours']
    list_per_page = 20
    date_hierarchy = 'date_attribution'
    
    def get_type_cours(self, obj):
        return obj.get_type_cours()
    get_type_cours.short_description = 'Type'
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('code_attribution', 'matricule_en', 'annee_academique')
        }),
        ('Attribution', {
            'fields': ('code_cours', 'type_charge'),
            'description': 'Attribuez un cours à l\'enseignant'
        }),
    )


@admin.register(DocumentCours)
class DocumentCoursAdmin(admin.ModelAdmin):
    list_display = ['titre', 'code_cours', 'type_document', 'enseignant', 'annee_academique', 'date_ajout']
    list_filter = ['type_document', 'annee_academique']
    search_fields = ['titre', 'code_cours', 'enseignant__nom_complet']


@admin.register(Deliberation)
class DeliberationAdmin(admin.ModelAdmin):
    list_display = [
        'matricule_etudiant',
        'code_ue',
        'code_ec',
        'type_deliberation',
        'annee_academique',
        'semestre',
        'statut',
        'cc',
        'examen',
        'date_creation',
        'cree_par'
    ]
    list_filter = [
        'type_deliberation',
        'annee_academique',
        'semestre',
        'statut',
        'code_classe',
        'date_creation'
    ]
    search_fields = [
        'matricule_etudiant__matricule_et',
        'matricule_etudiant__nom_complet',
        'code_ue__code_ue',
        'code_ec__code_ec',
        'annee_academique'
    ]
    list_per_page = 25
    readonly_fields = ['date_creation', 'date_mise_a_jour']
    
    fieldsets = (
        ('Informations sur l\'étudiant et le cours', {
            'fields': ('matricule_etudiant', 'code_ue', 'code_ec')
        }),
        ('Notes', {
            'fields': ('cc', 'examen', 'rattrapage', 'rachat')
        }),
        ('Informations de délibération', {
            'fields': ('type_deliberation', 'annee_academique', 'code_classe', 'semestre', 'statut')
        }),
        ('Métadonnées', {
            'fields': ('cree_par', 'date_creation', 'date_mise_a_jour'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'matricule_etudiant',
            'code_ue',
            'code_ec',
            'code_classe',
            'cree_par'
        )
