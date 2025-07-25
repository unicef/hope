# Generated by Django 3.2.25 on 2024-11-07 12:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0001_migration"),
        ("program", "0001_migration"),
    ]

    operations = [
        migrations.CreateModel(
            name="PeriodicDataUpdateTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "curr_async_result_id",
                    models.CharField(blank=True, help_text="Current (active) AsyncResult is", max_length=36, null=True),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("TO_EXPORT", "To export"),
                            ("NOT_SCHEDULED", "Not scheduled"),
                            ("EXPORTING", "Exporting"),
                            ("EXPORTED", "Exported"),
                            ("FAILED", "Failed"),
                            ("CANCELED", "Canceled"),
                        ],
                        default="TO_EXPORT",
                        max_length=20,
                    ),
                ),
                ("filters", models.JSONField(blank=True, default=dict, null=True)),
                ("rounds_data", models.JSONField()),
                ("number_of_records", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "business_area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="periodic_data_update_templates",
                        to="core.businessarea",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="periodic_data_updates_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "file",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="core.filetemp",
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="periodic_data_update_templates",
                        to="program.program",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PeriodicDataUpdateUpload",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "curr_async_result_id",
                    models.CharField(blank=True, help_text="Current (active) AsyncResult is", max_length=36, null=True),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("NOT_SCHEDULED", "Not scheduled"),
                            ("PROCESSING", "Processing"),
                            ("SUCCESSFUL", "Successful"),
                            ("FAILED", "Failed"),
                            ("CANCELED", "Canceled"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("file", models.FileField(upload_to="")),
                ("error_message", models.TextField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="periodic_data_update_uploads",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "template",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="uploads",
                        to="periodic_data_update.periodicdataupdatetemplate",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
