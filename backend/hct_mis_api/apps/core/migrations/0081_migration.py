# Generated by Django 3.2.25 on 2024-07-18 14:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0080_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flexibleattribute',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='flex_attributes', to='core.flexibleattributegroup'),
        ),
    ]