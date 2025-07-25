# Generated by Django 3.2.25 on 2025-01-16 10:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("household", "0006_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="household",
            name="internal_data",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="individual",
            name="internal_data",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
