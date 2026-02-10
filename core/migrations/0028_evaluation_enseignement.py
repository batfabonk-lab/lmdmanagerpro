from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_communique_deliberation_commentaire_cours'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluationEnseignement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annee_academique', models.CharField(max_length=20, verbose_name='Année Académique')),
                ('ponctualite', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Ponctualité')),
                ('maitrise_communication', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Maîtrise & communication')),
                ('pedagogie_methodologie', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Sens pédagogique & méthodologie')),
                ('utilisation_tic', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Utilisation des TIC')),
                ('disponibilite', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Disponibilité aux contacts')),
                ('commentaire', models.TextField(blank=True, default='', verbose_name='Commentaire')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('attribution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.attribution', verbose_name='Attribution')),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.etudiant', verbose_name='Étudiant')),
            ],
            options={
                'verbose_name': "Évaluation de l'enseignement",
                'verbose_name_plural': "Évaluations de l'enseignement",
                'ordering': ['-date_creation'],
                'unique_together': {('etudiant', 'attribution')},
            },
        ),
    ]
