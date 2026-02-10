from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


# Modèle d'utilisateur personnalisé
class User(AbstractUser):
    ROLE_CHOICES = [
        ('ETUDIANT', 'Étudiant'),
        ('ENSEIGNANT', 'Enseignant'),
        ('JURY', 'Jury'),
        ('ADMIN', 'Administrateur'),
        ('GESTIONNAIRE', 'Gestionnaire'),
        ('AGENT', 'Agent'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ETUDIANT')
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'


# Section
class Section(models.Model):
    code_section = models.CharField(max_length=20, primary_key=True, verbose_name='Code Section')
    designation_sc = models.CharField(max_length=200, verbose_name='Désignation')
    
    class Meta:
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
    
    def __str__(self):
        return f"{self.code_section} - {self.designation_sc}"


# Département
class Departement(models.Model):
    code_dpt = models.CharField(max_length=20, primary_key=True, verbose_name='Code Département')
    designation_dpt = models.CharField(max_length=200, verbose_name='Désignation')
    code_section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name='Section')
    
    class Meta:
        verbose_name = 'Département'
        verbose_name_plural = 'Départements'
    
    def __str__(self):
        return f"{self.code_dpt} - {self.designation_dpt}"


# Unité d'Enseignement (UE)
class UE(models.Model):
    CATEGORIE_CHOICES = [
        ('A', 'Catégorie A'),
        ('B', 'Catégorie B'),
    ]
    
    code_ue = models.CharField(max_length=20, primary_key=True, verbose_name='Code UE')
    intitule_ue = models.CharField(max_length=200, verbose_name='Intitulé')
    credit = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Crédits')
    semestre = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], verbose_name='Semestre')
    seuil = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Seuil', default=50)
    categorie = models.CharField(max_length=1, choices=CATEGORIE_CHOICES, default='A', verbose_name='Catégorie')
    classe = models.ForeignKey('reglage.Classe', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Classe')
    
    class Meta:
        verbose_name = 'Unité d\'Enseignement'
        verbose_name_plural = 'Unités d\'Enseignement'
    
    def __str__(self):
        return f"{self.code_ue} - {self.intitule_ue}"


# Élément Constitutif (EC)
class EC(models.Model):
    code_ec = models.CharField(max_length=20, primary_key=True, verbose_name='Code EC')
    intitule_ue = models.CharField(max_length=200, verbose_name='Intitulé')
    credit = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Crédits')
    code_ue = models.ForeignKey(UE, on_delete=models.CASCADE, verbose_name='UE')
    seuil = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Seuil', default=8)
    categorie = models.CharField(max_length=20, blank=True, null=True, verbose_name='Catégorie')
    classe = models.ForeignKey('reglage.Classe', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Classe')
    
    class Meta:
        verbose_name = 'Élément Constitutif'
        verbose_name_plural = 'Éléments Constitutifs'
    
    def __str__(self):
        return f"{self.code_ec} - {self.intitule_ue}"


# Cours pour Attribution (UE sans EC + tous les EC)
class CoursAttribution(models.Model):
    TYPE_CHOICES = [
        ('UE', 'Unité d\'Enseignement'),
        ('EC', 'Élément Constitutif'),
    ]
    
    code_cours = models.CharField(max_length=20, primary_key=True, verbose_name='Code Cours')
    intitule = models.CharField(max_length=200, verbose_name='Intitulé')
    type_cours = models.CharField(max_length=2, choices=TYPE_CHOICES, verbose_name='Type')
    code_ue_parent = models.CharField(max_length=20, blank=True, null=True, verbose_name='Code UE Parent')
    credit = models.IntegerField(verbose_name='Crédits')
    semestre = models.IntegerField(verbose_name='Semestre')
    classe = models.ForeignKey('reglage.Classe', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Classe')
    
    class Meta:
        verbose_name = 'Cours Attribution'
        verbose_name_plural = 'Cours Attributions'
        db_table = 'cours_attribution'
    
    def __str__(self):
        return f"{self.code_cours} - {self.intitule}"


# Cohorte
class Cohorte(models.Model):
    code_cohorte = models.CharField(max_length=20, primary_key=True, verbose_name='Code Cohorte')
    lib_cohorte = models.CharField(max_length=200, verbose_name='Libellé')
    debut = models.DateField(verbose_name='Date de début')
    
    class Meta:
        verbose_name = 'Cohorte'
        verbose_name_plural = 'Cohortes'
    
    def __str__(self):
        return f"{self.code_cohorte} - {self.lib_cohorte}"


# Liste des nationalités
NATIONALITES = [
    ('Congolaise (RDC)', 'Congolaise (RDC)'),
    ('Congolaise (Congo-Brazzaville)', 'Congolaise (Congo-Brazzaville)'),
    ('Angolaise', 'Angolaise'),
    ('Rwandaise', 'Rwandaise'),
    ('Burundaise', 'Burundaise'),
    ('Ougandaise', 'Ougandaise'),
    ('Tanzanienne', 'Tanzanienne'),
    ('Kenyane', 'Kenyane'),
    ('Sud-Africaine', 'Sud-Africaine'),
    ('Camerounaise', 'Camerounaise'),
    ('Nigériane', 'Nigériane'),
    ('Sénégalaise', 'Sénégalaise'),
    ('Ivoirienne', 'Ivoirienne'),
    ('Gabonaise', 'Gabonaise'),
    ('Centrafricaine', 'Centrafricaine'),
    ('Tchadienne', 'Tchadienne'),
    ('Zambienne', 'Zambienne'),
    ('Française', 'Française'),
    ('Belge', 'Belge'),
    ('Américaine', 'Américaine'),
    ('Chinoise', 'Chinoise'),
    ('Indienne', 'Indienne'),
    ('Autre', 'Autre'),
]

# Étudiant
class Etudiant(models.Model):
    matricule_et = models.CharField(max_length=20, primary_key=True, verbose_name='Matricule')
    nom_complet = models.CharField(max_length=200, verbose_name='Nom Complet')
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')], verbose_name='Sexe')
    date_naiss = models.DateField(verbose_name='Date de Naissance')
    nationalite = models.CharField(max_length=100, choices=NATIONALITES, default='Congolaise (RDC)', verbose_name='Nationalité')
    telephone = models.CharField(max_length=20, verbose_name='Téléphone')
    photo = models.ImageField(upload_to='etudiants/', blank=True, null=True, verbose_name='Photo')
    id_lgn = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Compte Utilisateur')
    
    class Meta:
        verbose_name = 'Étudiant'
        verbose_name_plural = 'Étudiants'
    
    def __str__(self):
        return f"{self.matricule_et} - {self.nom_complet}"
    
    def se_connecter(self):
        """Méthode pour se connecter au système"""
        pass
    
    def consulter(self):
        """Méthode pour consulter les résultats"""
        pass


# Enseignant
class Enseignant(models.Model):
    matricule_en = models.CharField(max_length=20, primary_key=True, verbose_name='Matricule')
    nom_complet = models.CharField(max_length=200, verbose_name='Nom Complet')
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Téléphone')
    fonction = models.ForeignKey('reglage.Fonction', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Fonction')
    grade = models.ForeignKey('reglage.Grade', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Grade')
    categorie = models.ForeignKey('reglage.Categorie', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Catégorie')
    code_dpt = models.ForeignKey('reglage.Departement', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Département')
    code_section = models.ForeignKey('reglage.Section', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Section')
    photo = models.ImageField(upload_to='enseignants/', blank=True, null=True, verbose_name='Photo')
    id_lgn = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Compte Utilisateur')
    
    class Meta:
        verbose_name = 'Enseignant'
        verbose_name_plural = 'Enseignants'
    
    def __str__(self):
        return f"{self.matricule_en} - {self.nom_complet}"
    
    @property
    def section(self):
        """Retourne la section du département"""
        if self.code_dpt:
            return self.code_dpt.code_section
        return None
    
    def se_connecter(self):
        """Méthode pour se connecter au système"""
        pass
    
    def encoder(self):
        """Méthode pour encoder les notes"""
        pass


# Classe
class Classe(models.Model):
    code_classe = models.CharField(max_length=20, primary_key=True, verbose_name='Code Classe')
    designation_cl = models.CharField(max_length=200, verbose_name='Désignation')
    
    class Meta:
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
    
    def __str__(self):
        return f"{self.code_classe} - {self.designation_cl}"




# Inscription
class Inscription(models.Model):
    code_inscription = models.CharField(max_length=20, primary_key=True, verbose_name='Code Inscription')
    matricule_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, verbose_name='Étudiant')
    annee_academique = models.CharField(max_length=20, verbose_name='Année Académique')
    code_classe = models.ForeignKey('reglage.Classe', on_delete=models.CASCADE, verbose_name='Classe')
    cohorte = models.ForeignKey(Cohorte, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Cohorte')

    class Meta:
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        unique_together = ['annee_academique', 'matricule_etudiant']
    
    def __str__(self):
        return f"{self.code_inscription} - {self.matricule_etudiant} ({self.annee_academique})"


# Jury
class Jury(models.Model):
    code_jury = models.CharField(max_length=20, primary_key=True, verbose_name='Code Jury')
    president = models.CharField(max_length=200, verbose_name='Président')
    secretaire = models.CharField(max_length=200, verbose_name='Secrétaire')
    membre = models.CharField(max_length=200, verbose_name='Membre')
    code_classe = models.ForeignKey('reglage.Classe', on_delete=models.CASCADE, verbose_name='Classe')
    annee_academique = models.CharField(max_length=20, verbose_name='Année Académique', blank=True, null=True)
    id_lgn = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Compte Utilisateur')
    decision = models.CharField(max_length=200, blank=True, null=True, verbose_name='Décision DG (nomination des membres)')
    
    class Meta:
        verbose_name = 'Jury'
        verbose_name_plural = 'Jurys'
    
    def __str__(self):
        return f"{self.code_jury} - {self.code_classe}"
    
    def get_president_display(self):
        """Récupère le nom complet du président"""
        try:
            enseignant = Enseignant.objects.get(matricule_en=self.president)
            return f"{enseignant.nom_complet} ({self.president})"
        except Enseignant.DoesNotExist:
            return self.president
    
    def get_secretaire_display(self):
        """Récupère le nom complet du secrétaire"""
        try:
            enseignant = Enseignant.objects.get(matricule_en=self.secretaire)
            return f"{enseignant.nom_complet} ({self.secretaire})"
        except Enseignant.DoesNotExist:
            return self.secretaire
    
    def get_membre_display(self):
        """Récupère le nom complet du membre"""
        try:
            enseignant = Enseignant.objects.get(matricule_en=self.membre)
            return f"{enseignant.nom_complet} ({self.membre})"
        except Enseignant.DoesNotExist:
            return self.membre
    
    def se_connecter(self):
        """Méthode pour se connecter au système"""
        pass
    
    def deliberer(self):
        """Méthode pour délibérer sur les résultats"""
        pass
    
    def publier(self):
        """Méthode pour publier les résultats"""
        pass


# Évaluation
class Evaluation(models.Model):
    TYPE_EVALUATION = [
        ('CC', 'Contrôle Continu'),
        ('EXAMEN', 'Examen'),
        ('RATTRAPAGE', 'Rattrapage'),
        ('RACHAT', 'Rachat'),
    ]
    
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('VALIDE', 'Validé'),
        ('NON_VALIDE', 'Non validé'),
    ]
    
    id_ev = models.AutoField(primary_key=True, verbose_name='ID Évaluation')
    cc = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(20)], verbose_name='Note CC', null=True, blank=True)
    examen = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(20)], verbose_name='Note Examen', null=True, blank=True)
    rattrapage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(20)], blank=True, null=True, verbose_name='Note Rattrapage')
    rachat = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(20)], blank=True, null=True, verbose_name='Note Rachat')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_COURS', verbose_name='Statut')
    code_ue = models.ForeignKey(UE, on_delete=models.CASCADE, verbose_name='UE', null=True, blank=True)
    matricule_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, verbose_name='Étudiant')
    code_ec = models.ForeignKey(EC, on_delete=models.CASCADE, verbose_name='EC', null=True, blank=True)
    code_classe = models.ForeignKey('reglage.Classe', on_delete=models.CASCADE, verbose_name='Classe', null=True, blank=True)
    annee_academique = models.CharField(max_length=10, verbose_name='Année Académique', default='2025-2026')
    
    # Champs de suivi des modifications par le jury
    modifie_par_jury = models.BooleanField(default=False, verbose_name='Modifié par le jury')
    jury_modificateur = models.CharField(max_length=200, blank=True, null=True, verbose_name='Membre du jury ayant modifié')
    date_modification_jury = models.DateTimeField(blank=True, null=True, verbose_name='Date de modification par le jury')
    ancien_cc = models.FloatField(blank=True, null=True, verbose_name='Ancien CC (avant modification jury)')
    ancien_examen = models.FloatField(blank=True, null=True, verbose_name='Ancien Examen (avant modification jury)')
    ancien_rattrapage = models.FloatField(blank=True, null=True, verbose_name='Ancien Rattrapage (avant modification jury)')
    ancien_rachat = models.FloatField(blank=True, null=True, verbose_name='Ancien Rachat (avant modification jury)')
    
    class Meta:
        verbose_name = 'Évaluation'
        verbose_name_plural = 'Évaluations'
        unique_together = ['matricule_etudiant', 'code_ue', 'code_ec', 'annee_academique', 'code_classe']
    
    def __str__(self):
        return f"{self.matricule_etudiant} - {self.code_ue} - {self.code_ec}"
    
    def calculer_note_finale(self):
        """Calcule la note finale (CC + Examen)"""
        if self.cc is None or self.examen is None:
            return None
        
        # Note finale = CC + Examen (sur 20)
        note_finale = self.cc + self.examen
        
        # Si rattrapage existe et > note_finale, on prend le rattrapage
        if self.rattrapage and self.rattrapage > note_finale:
            note_finale = self.rattrapage
        
        # Si rachat existe, on prend le rachat
        if self.rachat:
            note_finale = self.rachat
        
        # Arrondir à 1 décimale et garantir le formatage correct
        note_arrondie = round(note_finale, 1)
        return float(f"{note_arrondie:.1f}")
    
    def valider_statut(self):
        """Valide ou invalide l'évaluation selon la note finale (CC + Examen >= 10)"""
        if self.cc is not None and self.examen is not None:
            note_finale = self.cc + self.examen
            # Prendre en compte rattrapage si > note_finale
            if self.rattrapage and self.rattrapage > note_finale:
                note_finale = self.rattrapage
            # Prendre en compte rachat
            if self.rachat:
                note_finale = self.rachat
            
            if note_finale >= 10:
                self.statut = 'VALIDE'
            else:
                self.statut = 'NON_VALIDE'
    
    def save(self, *args, **kwargs):
        """Override save pour calculer automatiquement le statut"""
        self.valider_statut()
        super().save(*args, **kwargs)


# Inscription UE (pour les dettes des étudiants compensés)
class InscriptionUE(models.Model):
    TYPE_CHOICES = [
        ('DETTE_COMPENSEE', 'Dette compensée (à reprendre)'),
    ]
    
    code_inscription_ue = models.AutoField(primary_key=True, verbose_name='ID Inscription UE')
    matricule_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, verbose_name='Étudiant')
    code_ue = models.ForeignKey(UE, on_delete=models.CASCADE, verbose_name='UE', null=True, blank=True)
    code_ec = models.ForeignKey(EC, on_delete=models.CASCADE, verbose_name='EC', null=True, blank=True)
    annee_academique = models.CharField(max_length=10, verbose_name='Année Académique')
    code_classe = models.ForeignKey('reglage.Classe', on_delete=models.CASCADE, verbose_name="Classe d'origine (dette)")
    type_inscription = models.CharField(max_length=30, choices=TYPE_CHOICES, default='DETTE_COMPENSEE', verbose_name='Type')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    
    class Meta:
        verbose_name = 'Inscription UE (Dette)'
        verbose_name_plural = 'Inscriptions UE (Dettes)'
        unique_together = ['matricule_etudiant', 'code_ue', 'code_ec', 'annee_academique', 'code_classe']
    
    def __str__(self):
        ue_code = self.code_ue.code_ue if self.code_ue else (self.code_ec.code_ec if self.code_ec else 'N/A')
        return f"{self.matricule_etudiant} - {ue_code} - {self.annee_academique} (Dette {self.code_classe})"


class Attribution(models.Model):
    """Modèle pour attribuer des cours aux enseignants"""
    code_attribution = models.CharField(max_length=20, primary_key=True, verbose_name="Code Attribution")
    matricule_en = models.ForeignKey(Enseignant, on_delete=models.CASCADE, verbose_name="Enseignant")
    code_cours = models.CharField(max_length=20, verbose_name="Code Cours", default='')
    type_charge = models.ForeignKey('reglage.TypeCharge', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Type Charge")
    annee_academique = models.CharField(max_length=20, verbose_name="Année Académique")
    date_attribution = models.DateField(auto_now_add=True, verbose_name="Date d'Attribution")
    envoye_au_jury = models.BooleanField(default=False, verbose_name="Envoyé au jury")
    date_envoi_jury = models.DateTimeField(null=True, blank=True, verbose_name="Date d'envoi au jury")
    
    class Meta:
        verbose_name = "Attribution"
        verbose_name_plural = "Attributions"
        ordering = ['-date_attribution']
    
    def __str__(self):
        return f"{self.matricule_en} - {self.code_cours} ({self.annee_academique})"
    
    def get_cours_object(self):
        """Retourne l'objet UE ou EC correspondant au code_cours"""
        # Chercher d'abord dans UE
        try:
            return UE.objects.get(code_ue=self.code_cours)
        except UE.DoesNotExist:
            pass
        # Sinon chercher dans EC
        try:
            return EC.objects.get(code_ec=self.code_cours)
        except EC.DoesNotExist:
            return None
    
    def get_type_cours(self):
        """Retourne 'UE' ou 'EC' selon où se trouve le code"""
        if UE.objects.filter(code_ue=self.code_cours).exists():
            return 'UE'
        elif EC.objects.filter(code_ec=self.code_cours).exists():
            return 'EC'
        return None
    
    def get_intitule(self):
        """Retourne l'intitulé du cours"""
        cours = self.get_cours_object()
        if cours:
            if hasattr(cours, 'intitule_ue'):
                return cours.intitule_ue
        return self.code_cours


class ParametreEvaluation(models.Model):
    """Paramètres d'évaluation activés par le Jury pour une classe/année"""
    code_classe = models.ForeignKey('reglage.Classe', on_delete=models.CASCADE, verbose_name="Classe")
    annee_academique = models.CharField(max_length=20, verbose_name="Année Académique")
    rattrapage_actif = models.BooleanField(default=False, verbose_name="Rattrapage activé")
    rachat_actif = models.BooleanField(default=False, verbose_name="Rachat activé")
    date_activation_rattrapage = models.DateTimeField(null=True, blank=True, verbose_name="Date activation rattrapage")
    date_activation_rachat = models.DateTimeField(null=True, blank=True, verbose_name="Date activation rachat")
    active_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Activé par")
    
    class Meta:
        verbose_name = "Paramètre d'évaluation"
        verbose_name_plural = "Paramètres d'évaluation"
        unique_together = ['code_classe', 'annee_academique']
    
    def __str__(self):
        return f"{self.code_classe} - {self.annee_academique}"


class CommuniqueDeliberation(models.Model):
    code_classe = models.ForeignKey('reglage.Classe', on_delete=models.CASCADE, verbose_name='Classe')
    annee_academique = models.CharField(max_length=20, verbose_name='Année Académique')
    date_deliberation = models.DateField(verbose_name='Date de délibération')
    contenu = models.TextField(blank=True, default='', verbose_name='Communiqué')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Créé par')

    class Meta:
        verbose_name = 'Communiqué de délibération'
        verbose_name_plural = 'Communiqués de délibération'
        ordering = ['-date_deliberation', '-date_creation']
        unique_together = ['code_classe', 'annee_academique', 'date_deliberation']

    def __str__(self):
        return f"{self.code_classe} - {self.annee_academique} - {self.date_deliberation}"


# Délibération (clone du modèle Évaluation)
class Deliberation(models.Model):
    TYPE_EVALUATION = [
        ('CC', 'Contrôle Continu'),
        ('EXAMEN', 'Examen'),
        ('RATTRAPAGE', 'Rattrapage'),
        ('RACHAT', 'Rachat'),
    ]
    
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('VALIDE', 'Validé'),
        ('NON_VALIDE', 'Non validé'),
    ]
    
    TYPE_DELIB_CHOICES = [
        ('S1', 'Semestre 1'),
        ('S2', 'Semestre 2'),
        ('ANNEE', 'Année'),
    ]
    
    id_delib = models.AutoField(primary_key=True, verbose_name='ID Délibération')
    cc = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(20)], verbose_name='Note CC', null=True, blank=True)
    examen = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(20)], verbose_name='Note Examen', null=True, blank=True)
    rattrapage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(20)], blank=True, null=True, verbose_name='Note Rattrapage')
    rachat = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(20)], blank=True, null=True, verbose_name='Note Rachat')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_COURS', verbose_name='Statut')
    code_ue = models.ForeignKey(UE, on_delete=models.CASCADE, verbose_name='UE', null=True, blank=True)
    matricule_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, verbose_name='Étudiant')
    code_ec = models.ForeignKey(EC, on_delete=models.CASCADE, verbose_name='EC', null=True, blank=True)
    
    # Champs pour la délibération
    type_deliberation = models.CharField(max_length=10, choices=TYPE_DELIB_CHOICES, null=True, blank=True, verbose_name='Type de délibération')
    annee_academique = models.CharField(max_length=20, null=True, blank=True, verbose_name='Année Académique')
    code_classe = models.ForeignKey('reglage.Classe', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Classe')
    semestre = models.IntegerField(null=True, blank=True, verbose_name='Semestre')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour')
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Créé par')
    
    class Meta:
        verbose_name = 'Délibération'
        verbose_name_plural = 'Délibérations'
        unique_together = ['matricule_etudiant', 'code_ue', 'code_ec', 'type_deliberation', 'annee_academique']
    
    def __str__(self):
        return f"{self.matricule_etudiant} - {self.code_ue} - {self.code_ec} - {self.type_deliberation}"
    
    def calculer_note_finale(self):
        """Calcule la note finale (CC + Examen) - même logique que Evaluation"""
        if self.cc is None or self.examen is None:
            return None
        
        # Note finale = CC + Examen (sur 20)
        note_finale = self.cc + self.examen
        
        # Si rattrapage existe et > note_finale, on prend le rattrapage
        if self.rattrapage and self.rattrapage > note_finale:
            note_finale = self.rattrapage
        
        # Si rachat existe, on prend le rachat
        if self.rachat:
            note_finale = self.rachat
        
        # Arrondir à 1 décimale et garantir le formatage correct
        return round(float(note_finale), 1)
    
    @classmethod
    def creer_depuis_evaluation(cls, evaluation, type_deliberation, user=None):
        """Crée une délibération depuis une évaluation"""
        from core.models import Inscription
        
        # Récupérer l'année académique depuis l'inscription de l'étudiant
        inscription = Inscription.objects.filter(
            matricule_etudiant=evaluation.matricule_etudiant
        ).first()
        
        annee_academique = inscription.annee_academique if inscription else '2024-2025'
        
        # Récupérer la classe depuis l'UE
        code_classe = None
        semestre = None
        if evaluation.code_ec and evaluation.code_ec.code_ue:
            code_classe = evaluation.code_ec.code_ue.classe
            semestre = evaluation.code_ec.code_ue.semestre
        elif evaluation.code_ue:
            code_classe = evaluation.code_ue.classe
            semestre = evaluation.code_ue.semestre
        
        # Créer la délibération
        deliberation = cls.objects.create(
            cc=evaluation.cc,
            examen=evaluation.examen,
            rattrapage=evaluation.rattrapage,
            rachat=evaluation.rachat,
            statut=evaluation.statut,
            code_ue=evaluation.code_ue,
            matricule_etudiant=evaluation.matricule_etudiant,
            code_ec=evaluation.code_ec,
            type_deliberation=type_deliberation,
            annee_academique=annee_academique,
            code_classe=code_classe,
            semestre=semestre,
            cree_par=user
        )
        
        return deliberation
    
    @classmethod
    def appliquer_compensation_et_statuts(cls, classe_obj, type_deliberation, semestre=None, user=None):
        """Applique la compensation et attribue les statuts pour toutes les délibérations"""
        from core.views import _jury_compute_delib_ues
        
        # Récupérer tous les étudiants de la classe
        from core.models import Inscription
        etudiants = Inscription.objects.filter(code_classe=classe_obj).values_list('matricule_etudiant', flat=True)
        
        for etudiant_id in etudiants:
            etudiant = cls.matricule_etudiant.field.related_model.objects.get(pk=etudiant_id)
            
            # Calculer les données de délibération avec compensation
            delib_data = _jury_compute_delib_ues(
                classe_obj, etudiant, type_deliberation, semestre
            )
            
            # Récupérer l'année académique
            inscription = Inscription.objects.filter(
                matricule_etudiant=etudiant,
                code_classe=classe_obj
            ).first()
            annee_academique = inscription.annee_academique if inscription else '2024-2025'
            
            # Supprimer les anciennes délibérations pour ce type
            cls.objects.filter(
                matricule_etudiant=etudiant,
                type_deliberation=type_deliberation,
                annee_academique=annee_academique
            ).delete()
            
            # Créer les nouvelles délibérations avec les statuts calculés
            for ue_code, ue_data in delib_data.get('ue_data', {}).items():
                # Pour chaque EC de l'UE
                for ec_code, ec_data in ue_data.get('ec_data', {}).items():
                    evaluation = ec_data.get('evaluation')
                    if evaluation:
                        deliberation = cls.objects.create(
                            cc=evaluation.cc,
                            examen=evaluation.examen,
                            rattrapage=evaluation.rattrapage,
                            rachat=evaluation.rachat,
                            statut='VALIDE' if ec_data.get('statut') == 'Validé' else 'NON_VALIDE',
                            code_ue=evaluation.code_ue,
                            matricule_etudiant=evaluation.matricule_etudiant,
                            code_ec=evaluation.code_ec,
                            type_deliberation=type_deliberation,
                            annee_academique=annee_academique,
                            code_classe=classe_obj,
                            semestre=semestre,
                            cree_par=user
                        )

    @classmethod
    def appliquer_compensation(cls, classe_obj, type_deliberation, annee_academique, semestre=None):
        """
        Applique la compensation sur les délibérations existantes.
        Critères de compensation:
        1. Moyenne de la catégorie >= 10
        2. Note du cours entre 8 et 9.99
        3. Statut actuel = NON_VALIDE
        
        Ne change jamais VALIDE -> NON_VALIDE, seulement NON_VALIDE -> VALIDE
        """
        from core.models import Inscription
        
        # Déterminer le type de délibération code
        if type_deliberation == 'annuel':
            type_delib_code = 'ANNEE'
        else:
            # Semestre impair (1,3,5,...) → S1, pair (2,4,6,...) → S2
            type_delib_code = 'S1' if semestre % 2 == 1 else 'S2'
        
        # Récupérer tous les étudiants de la classe
        etudiants = Inscription.objects.filter(
            code_classe=classe_obj,
            annee_academique=annee_academique
        ).values_list('matricule_etudiant', flat=True).distinct()
        
        compensations_appliquees = []
        
        for etudiant_id in etudiants:
            try:
                etudiant = Etudiant.objects.get(pk=etudiant_id)
            except Etudiant.DoesNotExist:
                continue
            
            # Récupérer toutes les délibérations de cet étudiant
            deliberations = cls.objects.filter(
                matricule_etudiant=etudiant,
                code_classe=classe_obj,
                type_deliberation=type_delib_code,
                annee_academique=annee_academique
            ).select_related('code_ec', 'code_ec__code_ue', 'code_ue')
            
            if not deliberations.exists():
                continue
            
            # Calculer les moyennes par catégorie
            points_cat_a = 0
            credits_cat_a = 0
            points_cat_b = 0
            credits_cat_b = 0
            
            for delib in deliberations:
                note = delib.calculer_note_finale()
                if note is None:
                    continue
                
                # Déterminer le crédit et la catégorie
                ec = delib.code_ec
                ue = delib.code_ue if delib.code_ue else (ec.code_ue if ec else None)
                
                if ec and ec.credit:
                    credit = ec.credit
                elif ue and ue.credit:
                    credit = ue.credit
                else:
                    credit = 0
                
                categorie = ue.categorie if ue else ''
                
                if credit > 0:
                    if categorie == 'A':
                        points_cat_a += note * credit
                        credits_cat_a += credit
                    elif categorie == 'B':
                        points_cat_b += note * credit
                        credits_cat_b += credit
            
            # Calculer les moyennes
            moyenne_cat_a = points_cat_a / credits_cat_a if credits_cat_a > 0 else 0
            moyenne_cat_b = points_cat_b / credits_cat_b if credits_cat_b > 0 else 0
            
            # Appliquer la compensation
            for delib in deliberations:
                if delib.statut != 'NON_VALIDE':
                    continue  # Ne pas toucher aux VALIDE ou EN_COURS
                
                note = delib.calculer_note_finale()
                if note is None:
                    continue
                
                # Déterminer la catégorie
                ec = delib.code_ec
                ue = delib.code_ue if delib.code_ue else (ec.code_ue if ec else None)
                categorie = ue.categorie if ue else ''
                
                # Déterminer la moyenne de la catégorie
                if categorie == 'A':
                    moyenne_cat = moyenne_cat_a
                elif categorie == 'B':
                    moyenne_cat = moyenne_cat_b
                else:
                    moyenne_cat = 0
                
                # Critères de compensation: moyenne_cat >= 10 ET note entre 8 et 9.99
                if moyenne_cat >= 10 and 8 <= note < 10:
                    delib.statut = 'VALIDE'
                    delib.save(update_fields=['statut'])
                    compensations_appliquees.append({
                        'etudiant': str(etudiant),
                        'ec': ec.code_ec if ec else (ue.code_ue if ue else '-'),
                        'note': note,
                        'categorie': categorie,
                        'moyenne_cat': round(moyenne_cat, 2)
                    })
        
        return compensations_appliquees
    
    @classmethod
    def appliquer_compensation_annuelle(cls, classe_obj, annee_academique):
        """
        Applique la compensation annuelle sur les délibérations S1 et S2.
        Utilise les moyennes ANNUELLES par catégorie (combinant S1 et S2).
        
        Critères:
        1. Moyenne ANNUELLE de la catégorie >= 10
        2. Note du cours entre 8 et 9.99
        3. Statut actuel = NON_VALIDE
        
        Ne change jamais VALIDE -> NON_VALIDE
        """
        from core.models import Inscription
        
        # Récupérer tous les étudiants de la classe
        etudiants = Inscription.objects.filter(
            code_classe=classe_obj,
            annee_academique=annee_academique
        ).values_list('matricule_etudiant', flat=True).distinct()
        
        compensations_appliquees = []
        
        for etudiant_id in etudiants:
            try:
                etudiant = Etudiant.objects.get(pk=etudiant_id)
            except Etudiant.DoesNotExist:
                continue
            
            # Récupérer toutes les délibérations S1 et S2 de cet étudiant
            deliberations = cls.objects.filter(
                matricule_etudiant=etudiant,
                code_classe=classe_obj,
                type_deliberation__in=['S1', 'S2'],
                annee_academique=annee_academique
            ).select_related('code_ec', 'code_ec__code_ue', 'code_ue')
            
            if not deliberations.exists():
                continue
            
            # Calculer les moyennes ANNUELLES par catégorie (S1 + S2 combinés)
            points_cat_a = 0
            credits_cat_a = 0
            points_cat_b = 0
            credits_cat_b = 0
            
            for delib in deliberations:
                note = delib.calculer_note_finale()
                if note is None:
                    continue
                
                # Déterminer le crédit et la catégorie
                ec = delib.code_ec
                ue = delib.code_ue if delib.code_ue else (ec.code_ue if ec else None)
                
                if ec and ec.credit:
                    credit = ec.credit
                elif ue and ue.credit:
                    credit = ue.credit
                else:
                    credit = 0
                
                categorie = ue.categorie if ue else ''
                
                if credit > 0:
                    if categorie == 'A':
                        points_cat_a += note * credit
                        credits_cat_a += credit
                    elif categorie == 'B':
                        points_cat_b += note * credit
                        credits_cat_b += credit
            
            # Calculer les moyennes ANNUELLES
            moyenne_cat_a = points_cat_a / credits_cat_a if credits_cat_a > 0 else 0
            moyenne_cat_b = points_cat_b / credits_cat_b if credits_cat_b > 0 else 0
            
            # Appliquer la compensation annuelle
            for delib in deliberations:
                if delib.statut != 'NON_VALIDE':
                    continue  # Ne pas toucher aux VALIDE
                
                note = delib.calculer_note_finale()
                if note is None:
                    continue
                
                # Déterminer la catégorie
                ec = delib.code_ec
                ue = delib.code_ue if delib.code_ue else (ec.code_ue if ec else None)
                categorie = ue.categorie if ue else ''
                
                # Déterminer la moyenne ANNUELLE de la catégorie
                if categorie == 'A':
                    moyenne_cat = moyenne_cat_a
                elif categorie == 'B':
                    moyenne_cat = moyenne_cat_b
                else:
                    moyenne_cat = 0
                
                # Critères: moyenne_cat ANNUELLE >= 10 ET note entre 8 et 9.99
                if moyenne_cat >= 10 and 8 <= note < 10:
                    delib.statut = 'VALIDE'
                    delib.save(update_fields=['statut'])
                    compensations_appliquees.append({
                        'etudiant': str(etudiant),
                        'ec': ec.code_ec if ec else (ue.code_ue if ue else '-'),
                        'note': note,
                        'categorie': categorie,
                        'moyenne_cat_annuelle': round(moyenne_cat, 2),
                        'semestre': delib.type_deliberation
                    })
        
        return compensations_appliquees


class CommentaireCours(models.Model):
    TYPE_CHOICES = [
        ('UE', 'UE'),
        ('EC', 'EC'),
    ]

    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, verbose_name='Étudiant')
    annee_academique = models.CharField(max_length=20, verbose_name='Année Académique')
    type_cours = models.CharField(max_length=2, choices=TYPE_CHOICES, verbose_name='Type cours')
    code_cours = models.CharField(max_length=20, verbose_name='Code cours')
    contenu = models.TextField(verbose_name='Commentaire')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')

    class Meta:
        verbose_name = 'Commentaire de cours'
        verbose_name_plural = 'Commentaires de cours'
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.etudiant} - {self.code_cours}"


class EvaluationEnseignement(models.Model):
    NOTE_VALIDATORS = [MinValueValidator(1), MaxValueValidator(5)]

    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, verbose_name='Étudiant')
    attribution = models.ForeignKey(Attribution, on_delete=models.CASCADE, verbose_name='Attribution')
    annee_academique = models.CharField(max_length=20, verbose_name='Année Académique')

    ponctualite = models.PositiveSmallIntegerField(validators=NOTE_VALIDATORS, verbose_name='Ponctualité')
    maitrise_communication = models.PositiveSmallIntegerField(validators=NOTE_VALIDATORS, verbose_name='Maîtrise & communication')
    pedagogie_methodologie = models.PositiveSmallIntegerField(validators=NOTE_VALIDATORS, verbose_name='Sens pédagogique & méthodologie')
    utilisation_tic = models.PositiveSmallIntegerField(validators=NOTE_VALIDATORS, verbose_name='Utilisation des TIC')
    disponibilite = models.PositiveSmallIntegerField(validators=NOTE_VALIDATORS, verbose_name='Disponibilité aux contacts')

    commentaire = models.TextField(blank=True, default='', verbose_name='Commentaire')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')

    class Meta:
        verbose_name = "Évaluation de l'enseignement"
        verbose_name_plural = "Évaluations de l'enseignement"
        ordering = ['-date_creation']
        unique_together = ['etudiant', 'attribution']

    def __str__(self):
        return f"{self.etudiant} - {self.attribution}"

    def moyenne(self):
        return round(
            (
                float(self.ponctualite) +
                float(self.maitrise_communication) +
                float(self.pedagogie_methodologie) +
                float(self.utilisation_tic) +
                float(self.disponibilite)
            ) / 5,
            2
        )


class BulletinNotes(models.Model):
    """Bulletin de notes généré pour un étudiant après délibération"""
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, verbose_name='Étudiant')
    annee_academique = models.CharField(max_length=20, verbose_name='Année Académique')
    code_classe = models.ForeignKey('reglage.Classe', on_delete=models.CASCADE, verbose_name='Classe')
    fichier_pdf = models.FileField(upload_to='bulletins/', blank=True, null=True, verbose_name='Fichier PDF')
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name='Date de génération')
    genere_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Généré par')
    disponible = models.BooleanField(default=False, verbose_name='Disponible pour téléchargement')

    class Meta:
        verbose_name = 'Bulletin de notes'
        verbose_name_plural = 'Bulletins de notes'
        ordering = ['-date_generation']
        unique_together = ['etudiant', 'annee_academique', 'code_classe']


class Recours(models.Model):
    """Recours d'un étudiant concernant une note"""
    OBJET_CHOICES = [
        ('mauvaise_transcription_cc', 'Mauvaise transcription de CC'),
        ('mauvaise_transcription_examen', 'Mauvaise transcription d\'examen'),
        ('mauvais_calcul', 'Mauvais calcul de la note finale'),
        ('manque_cote', 'Manque de côte'),
        ('autre', 'Autre problème'),
    ]
    
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de traitement'),
        ('EN_EXAMEN', 'En cours d\'examen'),
        ('TRAITE', 'Traité'),
        ('REJETE', 'Rejeté'),
    ]
    
    code_recours = models.CharField(max_length=20, primary_key=True, verbose_name='Code Recours')
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, verbose_name='Étudiant')
    objet = models.CharField(max_length=30, choices=OBJET_CHOICES, verbose_name='Objet du recours')
    ue_ec_concerne = models.CharField(max_length=50, verbose_name='UE/EC concerné(e)')
    description = models.TextField(verbose_name='Description détaillée')
    date_envoi = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'envoi')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE', verbose_name='Statut')
    traite_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Traité par')
    date_traitement = models.DateTimeField(null=True, blank=True, verbose_name='Date de traitement')
    commentaire_traitement = models.TextField(blank=True, verbose_name='Commentaire de traitement')
    traitement_jury = models.TextField(blank=True, verbose_name='Traitement du jury')
    
    DECISION_FINALE_CHOICES = [
        ('', '---'),
        ('ACCEPTE', 'Accepté'),
        ('REJETE', 'Rejeté'),
        ('PARTIELLEMENT_ACCEPTE', 'Partiellement accepté'),
        ('SANS_SUITE', 'Classé sans suite'),
    ]
    decision_finale = models.CharField(max_length=30, choices=DECISION_FINALE_CHOICES, blank=True, default='', verbose_name='Décision finale')
    
    class Meta:
        verbose_name = 'Recours'
        verbose_name_plural = 'Recours'
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f"Recours {self.code_recours} - {self.etudiant.nom_complet}"
    
    def save(self, *args, **kwargs):
        if not self.code_recours:
            # Générer un code unique
            import uuid
            self.code_recours = f"REC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class FichierRecours(models.Model):
    """Fichiers joints à un recours"""
    recours = models.ForeignKey(Recours, on_delete=models.CASCADE, related_name='fichiers', verbose_name='Recours')
    fichier = models.FileField(upload_to='recours/', verbose_name='Fichier')
    nom_fichier = models.CharField(max_length=255, verbose_name='Nom du fichier')
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'ajout')
    
    class Meta:
        verbose_name = 'Fichier de recours'
        verbose_name_plural = 'Fichiers de recours'
        ordering = ['date_ajout']
    
    def __str__(self):
        return f"{self.nom_fichier} - {self.recours.code_recours}"
    
    def save(self, *args, **kwargs):
        if not self.nom_fichier:
            self.nom_fichier = self.fichier.name
        super().save(*args, **kwargs)


class Notification(models.Model):
    """Modèle pour stocker les notifications pour les utilisateurs"""
    TYPE_CHOICES = [
        ('COMMUNIQUE', 'Communiqué de délibération'),
        ('RESULTAT', 'Publication des résultats'),
        ('EVALUATION', 'Nouvelle évaluation'),
        ('MESSAGE', 'Message général'),
        ('SYSTEME', 'Notification système'),
    ]
    
    id_notification = models.AutoField(primary_key=True, verbose_name='ID Notification')
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Destinataire')
    type_notification = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Type de notification')
    titre = models.CharField(max_length=200, verbose_name='Titre')
    message = models.TextField(verbose_name='Message')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    lue = models.BooleanField(default=False, verbose_name='Lue')
    date_lecture = models.DateTimeField(null=True, blank=True, verbose_name='Date de lecture')
    lien = models.URLField(blank=True, null=True, verbose_name='Lien vers la ressource')
    
    # Référence optionnelle à l'objet concerné
    code_classe = models.ForeignKey('reglage.Classe', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Classe')
    annee_academique = models.CharField(max_length=20, blank=True, null=True, verbose_name='Année académique')
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Notification pour {self.destinataire.username} - {self.titre}"
    
    def marquer_comme_lue(self):
        """Marque la notification comme lue"""
        self.lue = True
        self.date_lecture = timezone.now()
        self.save(update_fields=['lue', 'date_lecture'])


# Historique des actions
class HistoriqueAction(models.Model):
    """Modèle pour tracer les actions (ajout, modification, suppression) des utilisateurs"""
    
    TYPE_ACTIONS = [
        ('CREATION', 'Création'),
        ('MODIFICATION', 'Modification'),
        ('SUPPRESSION', 'Suppression'),
    ]
    
    TYPES_OBJETS = [
        ('Etudiant', 'Étudiant'),
        ('Enseignant', 'Enseignant'),
        ('Jury', 'Jury'),
        ('Inscription', 'Inscription'),
        ('Attribution', 'Attribution'),
        ('UE', 'UE'),
        ('EC', 'EC'),
        ('Cohorte', 'Cohorte'),
        ('Classe', 'Classe'),
        ('Utilisateur', 'Utilisateur'),
        ('Autre', 'Autre'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Utilisateur')
    type_action = models.CharField(max_length=20, choices=TYPE_ACTIONS, verbose_name='Type d\'action')
    type_objet = models.CharField(max_length=50, choices=TYPES_OBJETS, verbose_name='Type d\'objet')
    objet_id = models.CharField(max_length=100, verbose_name='ID de l\'objet')
    objet_nom = models.CharField(max_length=255, verbose_name='Nom/Description de l\'objet')
    date_action = models.DateTimeField(auto_now_add=True, verbose_name='Date de l\'action')
    details = models.TextField(blank=True, null=True, verbose_name='Détails additionnels')
    adresse_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='Adresse IP')
    
    class Meta:
        verbose_name = 'Historique d\'Action'
        verbose_name_plural = 'Historiques d\'Actions'
        ordering = ['-date_action']
    
    def __str__(self):
        return f"{self.get_type_action_display()} - {self.type_objet} ({self.date_action.strftime('%d/%m/%Y %H:%M')})"

