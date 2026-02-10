# Generated manually to recreate Deliberation model as clone of Evaluation

from django.db import migrations, models
import django.db.models.deletion


def delete_old_deliberation(apps, schema_editor):
    """Delete old deliberation records before model recreation"""
    Deliberation = apps.get_model('core', 'Deliberation')
    Deliberation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_deliberation'),
    ]

    operations = [
        # Run Python function to delete all records
        migrations.RunPython(delete_old_deliberation, migrations.RunPython.noop),
        
        # Delete the old model
        migrations.DeleteModel(
            name='Deliberation',
        ),
        
        # Create the new deliberation model as clone of evaluation
        migrations.CreateModel(
            name='Deliberation',
            fields=[
                ('id_delib', models.AutoField(primary_key=True, serialize=False, verbose_name='ID Délibération')),
                ('cc', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(20)], verbose_name='Note CC')),
                ('examen', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(20)], verbose_name='Note Examen')),
                ('rattrapage', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(20)], verbose_name='Note Rattrapage')),
                ('rachat', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(20)], verbose_name='Note Rachat')),
                ('statut', models.CharField(choices=[('EN_COURS', 'En cours'), ('VALIDE', 'Validé'), ('NON_VALIDE', 'Non validé')], default='EN_COURS', max_length=20, verbose_name='Statut')),
                ('type_deliberation', models.CharField(choices=[('S1', 'Semestre 1'), ('S2', 'Semestre 2'), ('ANNEE', 'Année')], max_length=10, verbose_name='Type de délibération')),
                ('annee_academique', models.CharField(max_length=20, verbose_name='Année Académique')),
                ('semestre', models.IntegerField(blank=True, null=True, verbose_name='Semestre')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('date_mise_a_jour', models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour')),
                ('code_ue', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.ue', verbose_name='UE')),
                ('code_ec', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.ec', verbose_name='EC')),
                ('code_classe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reglage.classe', verbose_name='Classe')),
                ('cree_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user', verbose_name='Créé par')),
                ('matricule_etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.etudiant', verbose_name='Étudiant')),
            ],
            options={
                'verbose_name': 'Délibération',
                'verbose_name_plural': 'Délibérations',
                'unique_together': {('matricule_etudiant', 'code_ue', 'code_ec', 'type_deliberation', 'annee_academique')},
            },
        ),
    ]
