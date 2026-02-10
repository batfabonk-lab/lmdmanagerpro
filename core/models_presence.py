from django.db import models
from .models import Enseignant, User
from reglage.models import Classe


class PresenceDeliberation(models.Model):
    """Modèle pour enregistrer les présences des enseignants à la délibération"""
    STATUT_CHOICES = [
        ('present', 'Présent(e)'),
        ('absent', 'Absent(e)'),
        ('excuse', 'Excusé(e)'),
    ]
    
    code_classe = models.ForeignKey(Classe, on_delete=models.CASCADE, verbose_name='Classe')
    annee_academique = models.CharField(max_length=20, verbose_name='Année Académique')
    session = models.CharField(max_length=100, verbose_name='Session', default='Aout 2025')
    matricule_en = models.ForeignKey(Enseignant, on_delete=models.CASCADE, verbose_name='Enseignant')
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='present', verbose_name='Statut')
    date_deliberation = models.DateField(verbose_name='Date de délibération')
    observations = models.TextField(blank=True, default='', verbose_name='Observations du jury')
    decision_reference = models.CharField(max_length=100, blank=True, default='', verbose_name='Référence décision DG')
    enregistre_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Enregistré par')
    date_enregistrement = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'enregistrement')
    
    class Meta:
        verbose_name = 'Présence à la délibération'
        verbose_name_plural = 'Présences aux délibérations'
        unique_together = ['code_classe', 'annee_academique', 'matricule_en', 'date_deliberation']
        ordering = ['matricule_en__nom_complet']
    
    def __str__(self):
        return f"{self.matricule_en} - {self.code_classe} ({self.statut})"
