import concurrency.fields
from django.conf import settings
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion

import hope.models.rule
import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("steficon", "0001_migration"),
        ("steficon", "0002_migration"),
        ("steficon", "0003_migration"),
        ("steficon", "0004_migration"),
        ("steficon", "0005_migration"),
        ("steficon", "0006_migration"),
        ("steficon", "0007_migration"),
    ]

    dependencies = [
        ("core", "0044_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE COLLATION IF NOT EXISTS \"und-ci-det\" (provider = icu, locale = 'und-u-ks-level2', deterministic = true);",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name="Rule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "version",
                    concurrency.fields.AutoIncVersionField(default=0, help_text="record revision number"),
                ),
                (
                    "name",
                    models.CharField(
                        db_collation="und-ci-det",
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
                (
                    "language",
                    models.CharField(
                        choices=hope.models.rule.get_languages_choices,
                        default="python",
                        max_length=10,
                    ),
                ),
                (
                    "security",
                    models.IntegerField(choices=hope.models.rule.get_rule_security_choices, default=2),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "type",
                    models.CharField(
                        choices=hope.models.rule.get_rule_type_choices,
                        default="TARGETING",
                        help_text="Use Rule for Targeting or Payment Plan",
                        max_length=50,
                    ),
                ),
                ("flags", models.JSONField(blank=True, default=dict)),
                (
                    "allowed_business_areas",
                    models.ManyToManyField(blank=True, to="core.businessarea"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
                "permissions": (
                    ("process_file", "Can Process File"),
                    ("check_diff", "Can Check Diff"),
                    ("changelog", "Can Check Changelog"),
                    ("rerun_rule", "Can Rerun Rule"),
                ),
            },
        ),
        migrations.CreateModel(
            name="RuleCommit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now=True)),
                ("version", models.IntegerField()),
                ("definition", models.TextField(blank=True, default="result.value=0")),
                ("is_release", models.BooleanField(default=False)),
                ("enabled", models.BooleanField(default=False)),
                ("deprecated", models.BooleanField(default=False)),
                (
                    "language",
                    models.CharField(
                        choices=hope.models.rule.get_languages_choices,
                        default="python",
                        max_length=10,
                    ),
                ),
                (
                    "affected_fields",
                    django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=None),
                ),
                (
                    "before",
                    models.JSONField(
                        default=dict,
                        editable=False,
                        help_text="The record before change",
                    ),
                ),
                (
                    "after",
                    models.JSONField(
                        default=dict,
                        editable=False,
                        help_text="The record after apply changes",
                    ),
                ),
                (
                    "rule",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="history",
                        to="steficon.rule",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
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
            },
        ),
        migrations.AddIndex(
            model_name="rule",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="steficon_rule_created_at_80077537"),
        ),
        migrations.AddIndex(
            model_name="rule",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="steficon_rule_updated_at_8183c1cf"),
        ),
        migrations.AlterUniqueTogether(
            name="rulecommit",
            unique_together={("rule", "version")},
        ),
    ]
