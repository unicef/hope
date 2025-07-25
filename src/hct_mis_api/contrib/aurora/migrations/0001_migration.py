# Generated by Django 3.2.25 on 2024-11-07 12:18

import django.db.models.deletion
import strategy_field.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Record",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("registration", models.IntegerField(db_index=True)),
                ("timestamp", models.DateTimeField(db_index=True)),
                ("storage", models.BinaryField(blank=True, null=True)),
                ("ignored", models.BooleanField(blank=True, db_index=True, default=False, null=True)),
                ("source_id", models.IntegerField(db_index=True)),
                ("data", models.JSONField(blank=True, default=dict, null=True)),
                ("error_message", models.TextField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[("TO_IMPORT", "To import"), ("IMPORTED", "Imported"), ("ERROR", "Error")],
                        max_length=16,
                        null=True,
                    ),
                ),
                ("unique_field", models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ("size", models.IntegerField(blank=True, null=True)),
                ("counters", models.JSONField(blank=True, null=True)),
                ("fields", models.JSONField(blank=True, null=True)),
                ("files", models.BinaryField(blank=True, null=True)),
                ("index1", models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ("index2", models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ("index3", models.CharField(blank=True, db_index=True, max_length=255, null=True)),
            ],
            options={
                "swappable": "AURORA_RECORD_MODEL",
            },
        ),
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_id", models.BigIntegerField()),
                ("name", models.CharField(max_length=1000)),
                ("slug", models.SlugField(max_length=1000)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_id", models.BigIntegerField()),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Registration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_id", models.BigIntegerField()),
                ("name", models.CharField(max_length=500)),
                ("slug", models.SlugField()),
                ("extra", models.JSONField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, null=True)),
                (
                    "rdi_policy",
                    models.IntegerField(choices=[(1, "Manual"), (2, "Daily"), (3, "As data arrives")], default=1),
                ),
                ("rdi_parser", strategy_field.fields.StrategyField(blank=True, null=True)),
                ("mapping", models.JSONField(blank=True, null=True)),
                ("private_key", models.TextField(blank=True, editable=False, null=True)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="aurora.project")),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
