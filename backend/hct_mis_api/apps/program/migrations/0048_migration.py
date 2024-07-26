# Generated by Django 3.2.25 on 2024-07-17 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0047_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='programcycle',
            options={'ordering': ['start_date'], 'verbose_name': 'ProgrammeCycle'},
        ),
        migrations.AddField(
            model_name='programcycle',
            name='title',
            field=models.CharField(blank=True, default='Default Programme Cycle', max_length=255, null=True, verbose_name='Title'),
        ),
        migrations.AddField(
            model_name='programcycle',
            name='unicef_id',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='programcycle',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('ACTIVE', 'Active'), ('FINISHED', 'Finished')], db_index=True, default='DRAFT', max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='programcycle',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='programcycle',
            constraint=models.UniqueConstraint(condition=models.Q(('is_removed', False)), fields=('title', 'program', 'is_removed'), name='program_cycle_name_unique_if_not_removed'),
        ),
        migrations.RemoveField(
            model_name='programcycle',
            name='description',
        ),
        migrations.RemoveField(
            model_name='programcycle',
            name='iteration',
        ),
    ]