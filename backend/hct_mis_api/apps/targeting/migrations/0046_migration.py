# Generated by Django 3.2.25 on 2024-08-12 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targeting', '0045_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetingcriteriarulefilter',
            name='round_number',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='targetingindividualblockrulefilter',
            name='round_number',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='targetingcriteriarulefilter',
            name='comparison_method',
            field=models.CharField(choices=[('EQUALS', 'Equals'), ('NOT_EQUALS', 'Not Equals'), ('CONTAINS', 'Contains'), ('NOT_CONTAINS', 'Does not contain'), ('RANGE', 'In between <>'), ('NOT_IN_RANGE', 'Not in between <>'), ('GREATER_THAN', 'Greater than'), ('LESS_THAN', 'Less than'), ('IS_NULL', 'Is null')], max_length=20),
        ),
        migrations.AlterField(
            model_name='targetingindividualblockrulefilter',
            name='comparison_method',
            field=models.CharField(choices=[('EQUALS', 'Equals'), ('NOT_EQUALS', 'Not Equals'), ('CONTAINS', 'Contains'), ('NOT_CONTAINS', 'Does not contain'), ('RANGE', 'In between <>'), ('NOT_IN_RANGE', 'Not in between <>'), ('GREATER_THAN', 'Greater than'), ('LESS_THAN', 'Less than'), ('IS_NULL', 'Is null')], max_length=20),
        ),
    ]