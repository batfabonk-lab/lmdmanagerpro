from django.db import models


class Section(models.Model):
    """Modèle pour les sections"""
    code_section = models.CharField(max_length=20, primary_key=True, verbose_name="Code Section")
    designation_section = models.CharField(max_length=200, verbose_name="Désignation Section")
    
    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        ordering = ['code_section']
    
    def __str__(self):
        return f"{self.code_section} - {self.designation_section}"


class Departement(models.Model):
    """Modèle pour les départements"""
    code_departement = models.CharField(max_length=20, primary_key=True, verbose_name="Code Département")
    designation_departement = models.CharField(max_length=200, verbose_name="Désignation Département")
    code_section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name="Section")
    
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['code_departement']
    
    def __str__(self):
        return f"{self.code_departement} - {self.designation_departement}"


class Mention(models.Model):
    """Modèle pour les mentions"""
    code_mention = models.CharField(max_length=20, primary_key=True, verbose_name="Code Mention")
    designation_mention = models.CharField(max_length=200, verbose_name="Désignation Mention")
    
    class Meta:
        verbose_name = "Mention"
        verbose_name_plural = "Mentions"
        ordering = ['code_mention']
    
    def __str__(self):
        return f"{self.code_mention} - {self.designation_mention}"


class Niveau(models.Model):
    """Modèle pour les niveaux"""
    code_niveau = models.CharField(max_length=20, primary_key=True, verbose_name="Code Niveau")
    designation_niveau = models.CharField(max_length=200, verbose_name="Désignation Niveau")
    
    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"
        ordering = ['code_niveau']
    
    def __str__(self):
        return f"{self.code_niveau} - {self.designation_niveau}"


class Semestre(models.Model):
    """Modèle pour les semestres"""
    code_semestre = models.CharField(max_length=20, primary_key=True, verbose_name="Code Semestre")
    designation_semestre = models.CharField(max_length=200, verbose_name="Désignation Semestre")
    
    class Meta:
        verbose_name = "Semestre"
        verbose_name_plural = "Semestres"
        ordering = ['code_semestre']
    
    def __str__(self):
        return f"{self.code_semestre} - {self.designation_semestre}"


class Classe(models.Model):
    """Modèle pour les classes"""
    code_classe = models.CharField(max_length=40, primary_key=True, verbose_name="Code Classe")
    designation_classe = models.CharField(max_length=400, verbose_name="Désignation Classe")
    code_niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, verbose_name="Niveau", null=True)
    code_mention = models.ForeignKey(Mention, on_delete=models.CASCADE, verbose_name="Mention", null=True)
    
    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ['code_classe']
        unique_together = ['code_niveau', 'code_mention']
    
    def save(self, *args, **kwargs):
        # Générer automatiquement le code et la désignation
        if self.code_niveau and self.code_mention:
            self.code_classe = f"{self.code_niveau.code_niveau}{self.code_mention.code_mention}"
            self.designation_classe = f"{self.code_niveau.designation_niveau} {self.code_mention.designation_mention}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.code_classe


class AnneeAcademique(models.Model):
    """Modèle pour les années académiques"""
    code_anac = models.CharField(max_length=20, primary_key=True, verbose_name="Code Année Académique")
    designation_anac = models.CharField(max_length=200, verbose_name="Désignation Année Académique")
    date_debut = models.DateField(verbose_name="Date Début", null=True, blank=True)
    date_fin = models.DateField(verbose_name="Date Fin", null=True, blank=True)
    active = models.BooleanField(default=False, verbose_name="Année en cours")
    
    class Meta:
        verbose_name = "Année Académique"
        verbose_name_plural = "Années Académiques"
        ordering = ['-code_anac']
    
    def save(self, *args, **kwargs):
        # Si cette année est définie comme active, désactiver toutes les autres
        if self.active:
            AnneeAcademique.objects.filter(active=True).exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_annee_en_cours(cls):
        """Retourne l'année académique en cours"""
        return cls.objects.filter(active=True).first()
    
    def __str__(self):
        if self.active:
            return f"{self.code_anac} - {self.designation_anac} (En cours)"
        return f"{self.code_anac} - {self.designation_anac}"


class Grade(models.Model):
    """Modèle pour les grades des enseignants"""
    code_grade = models.CharField(max_length=20, primary_key=True, verbose_name="Code Grade")
    designation_grade = models.CharField(max_length=200, verbose_name="Désignation Grade")
    
    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        ordering = ['code_grade']
    
    def __str__(self):
        return f"{self.code_grade} - {self.designation_grade}"


class Fonction(models.Model):
    """Modèle pour les fonctions des enseignants"""
    code_fonction = models.CharField(max_length=20, primary_key=True, verbose_name="Code Fonction")
    designation_fonction = models.CharField(max_length=200, verbose_name="Désignation Fonction")
    
    class Meta:
        verbose_name = "Fonction"
        verbose_name_plural = "Fonctions"
        ordering = ['code_fonction']
    
    def __str__(self):
        return f"{self.code_fonction} - {self.designation_fonction}"


class TypeCharge(models.Model):
    """Modèle pour les types de charge"""
    code_type = models.CharField(max_length=20, primary_key=True, verbose_name="Code Type")
    designation_typecharge = models.CharField(max_length=200, verbose_name="Désignation Type Charge")
    
    class Meta:
        verbose_name = "Type de Charge"
        verbose_name_plural = "Types de Charge"
        ordering = ['code_type']
    
    def __str__(self):
        return f"{self.code_type} - {self.designation_typecharge}"


class Categorie(models.Model):
    """Modèle pour les catégories"""
    code_categorie = models.CharField(max_length=20, primary_key=True, verbose_name="Code Catégorie")
    designation_categorie = models.CharField(max_length=200, verbose_name="Désignation Catégorie")
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['code_categorie']
    
    def __str__(self):
        return f"{self.code_categorie} - {self.designation_categorie}"
