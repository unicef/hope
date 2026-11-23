import uuid

import django.contrib.postgres.fields
from django.db import migrations, models
import model_utils.fields

import hope.apps.core.upload_paths
import hope.models.feedback
import hope.models.message
import hope.models.survey
import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("accountability", "0002_migration"),
        ("accountability", "0003_migration"),
        ("accountability", "0004_migration"),
        ("accountability", "0005_migration"),
        ("accountability", "0006_migration"),
        ("accountability", "0007_migration"),
        ("accountability", "0008_migration"),
        ("accountability", "0009_migration"),
        ("accountability", "0010_migration"),
        ("accountability", "0011_migration"),
        ("accountability", "0012_migration"),
    ]

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Feedback",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("unicef_id", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "issue_type",
                    models.CharField(
                        choices=hope.models.feedback.get_issue_type_choices,
                        max_length=20,
                        verbose_name="Issue type",
                    ),
                ),
                ("area", models.CharField(blank=True, max_length=250)),
                ("description", models.TextField()),
                ("language", models.TextField(blank=True)),
                ("comments", models.TextField(blank=True, null=True)),
                ("consent", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Feedback",
                "ordering": ("created_at",),
            },
            bases=(hope.models.utils.AdminUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name="FeedbackMessage",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "description",
                    models.TextField(
                        help_text="The content of the feedback message.",
                        verbose_name="Description",
                    ),
                ),
            ],
            options={
                "verbose_name": "Feedback message",
                "ordering": ("created_at",),
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("unicef_id", models.CharField(blank=True, max_length=255, null=True)),
                ("title", models.CharField(max_length=60)),
                ("body", models.TextField(max_length=1000)),
                ("number_of_recipients", models.PositiveIntegerField(default=0)),
                (
                    "sampling_type",
                    models.CharField(
                        choices=hope.models.message.Message.SamplingChoices.get_choices,
                        default="FULL_LIST",
                        max_length=50,
                    ),
                ),
                ("full_list_arguments", models.JSONField(blank=True, null=True)),
                ("random_sampling_arguments", models.JSONField(blank=True, null=True)),
                ("sample_size", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Message",
                "ordering": ("created_at",),
            },
            bases=(hope.models.utils.AdminUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Survey",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("unicef_id", models.CharField(blank=True, max_length=255, null=True)),
                ("title", models.CharField(max_length=60)),
                ("body", models.TextField(blank=True, default="", max_length=1000)),
                (
                    "category",
                    models.CharField(choices=hope.models.survey.get_category_choices, max_length=16),
                ),
                ("number_of_recipients", models.PositiveIntegerField(default=0)),
                ("flow_id", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "sampling_type",
                    models.CharField(
                        choices=hope.models.survey.get_sampling_choices,
                        default="FULL_LIST",
                        max_length=50,
                    ),
                ),
                ("sample_size", models.PositiveIntegerField(default=0)),
                (
                    "sample_file",
                    models.FileField(
                        blank=True,
                        max_length=255,
                        null=True,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                (
                    "sample_file_generated_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("full_list_arguments", models.JSONField(blank=True, default=dict)),
                (
                    "random_sampling_arguments",
                    models.JSONField(blank=True, default=dict),
                ),
                (
                    "successful_rapid_pro_calls",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.JSONField(),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
            ],
            options={
                "verbose_name": "Survey",
                "ordering": ("created_at",),
            },
            bases=(hope.models.utils.AdminUrlMixin, models.Model),
        ),
    ]
