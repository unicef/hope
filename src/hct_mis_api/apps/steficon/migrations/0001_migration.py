# Generated by Django 3.2.25 on 2024-11-07 12:18

import concurrency.fields
import django.contrib.postgres.fields
import django.contrib.postgres.fields.citext
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0001_migration"),
    ]

    operations = [
        migrations.CreateModel(
            name="Rule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.AutoIncVersionField(default=0, help_text="record revision number")),
                (
                    "name",
                    django.contrib.postgres.fields.citext.CICharField(
                        max_length=100,
                        unique=True,
                        validators=[
                            django.core.validators.ProhibitNullCharactersValidator(),
                            django.core.validators.RegexValidator(
                                "(^\\s+)|(\\s+$)",
                                "Leading or trailing spaces characters are not allowed.",
                                code="leading_trailing_spaces_characters_not_allowed",
                                inverse_match=True,
                            ),
                            django.core.validators.RegexValidator(
                                "\\s{2,}",
                                "Double spaces characters are not allowed.",
                                code="double_spaces_characters_not_allowed",
                                inverse_match=True,
                            ),
                        ],
                    ),
                ),
                ("definition", models.TextField(blank=True, default="result.value=0")),
                ("description", models.TextField(blank=True, null=True)),
                ("enabled", models.BooleanField(default=False)),
                ("deprecated", models.BooleanField(default=False)),
                ("language", models.CharField(choices=[("python", "Python")], default="python", max_length=10)),
                ("security", models.IntegerField(choices=[(0, "Low"), (2, "Medium"), (4, "High")], default=2)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "type",
                    models.CharField(
                        choices=[("PAYMENT_PLAN", "Payment Plan"), ("TARGETING", "Targeting")],
                        default="TARGETING",
                        help_text="Use Rule for Targeting or Payment Plan",
                        max_length=50,
                    ),
                ),
                ("flags", models.JSONField(blank=True, default=dict)),
                ("allowed_business_areas", models.ManyToManyField(blank=True, to="core.BusinessArea")),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RuleCommit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("timestamp", models.DateTimeField(auto_now=True)),
                ("version", models.IntegerField()),
                ("definition", models.TextField(blank=True, default="result.value=0")),
                ("is_release", models.BooleanField(default=False)),
                ("enabled", models.BooleanField(default=False)),
                ("deprecated", models.BooleanField(default=False)),
                ("language", models.CharField(choices=[("python", "Python")], default="python", max_length=10)),
                (
                    "affected_fields",
                    django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=None),
                ),
                ("before", models.JSONField(default=dict, editable=False, help_text="The record before change")),
                ("after", models.JSONField(default=dict, editable=False, help_text="The record after apply changes")),
                (
                    "rule",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="history",
                        to="steficon.rule",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "RuleCommit",
                "verbose_name_plural": "Rule Commits",
                "ordering": ("-version",),
                "get_latest_by": "-version",
                "unique_together": {("rule", "version")},
            },
        ),
    ]
