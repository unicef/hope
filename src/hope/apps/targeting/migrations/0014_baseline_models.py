import uuid

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields

import hope.apps.targeting.choices
import hope.apps.targeting.services.targeting_service
import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("targeting", "0001_migration"),
        ("targeting", "0002_migration"),
        ("targeting", "0003_migration"),
        ("targeting", "0004_migration"),
        ("targeting", "0005_migration"),
        ("targeting", "0006_migration"),
        ("targeting", "0007_migration"),
        ("targeting", "0008_migration"),
        ("targeting", "0009_migration"),
        ("targeting", "0010_migration"),
        ("targeting", "0011_migration"),
        ("targeting", "0012_migration"),
        ("targeting", "0013_migration"),
    ]

    dependencies = [
        ("payment", "0081_baseline_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="TargetingCriteriaRule",
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
                ("household_ids", models.TextField(blank=True)),
                ("individual_ids", models.TextField(blank=True)),
                (
                    "alternative_collectors_ids",
                    models.TextField(blank=True, help_text="Use Alternative collectors for those IDs"),
                ),
                (
                    "payment_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rules",
                        to="payment.paymentplan",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
            bases=(
                models.Model,
                hope.apps.targeting.services.targeting_service.TargetingCriteriaRuleQueryingBase,
            ),
        ),
        migrations.CreateModel(
            name="TargetingCriteriaRuleFilter",
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
                    "comparison_method",
                    models.CharField(
                        choices=hope.apps.targeting.services.targeting_service.TargetingCriteriaFilterBase.get_comparison_choices,
                        max_length=20,
                    ),
                ),
                (
                    "flex_field_classification",
                    models.CharField(
                        choices=hope.apps.targeting.choices.FlexFieldClassification.get_choices,
                        default="NOT_FLEX_FIELD",
                        max_length=20,
                    ),
                ),
                ("field_name", models.CharField(max_length=50)),
                (
                    "arguments",
                    models.JSONField(help_text="\n                Array of arguments\n                "),
                ),
                ("round_number", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "targeting_criteria_rule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="filters",
                        to="targeting.targetingcriteriarule",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
            bases=(
                models.Model,
                hope.apps.targeting.services.targeting_service.TargetingCriteriaFilterBase,
            ),
        ),
        migrations.CreateModel(
            name="TargetingIndividualRuleFilterBlock",
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
                ("target_only_hoh", models.BooleanField(default=False)),
                (
                    "targeting_criteria_rule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="individuals_filters_blocks",
                        to="targeting.targetingcriteriarule",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
            bases=(
                models.Model,
                hope.apps.targeting.services.targeting_service.TargetingIndividualRuleFilterBlockBase,
            ),
        ),
        migrations.CreateModel(
            name="TargetingIndividualBlockRuleFilter",
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
                    "comparison_method",
                    models.CharField(
                        choices=hope.apps.targeting.services.targeting_service.TargetingCriteriaFilterBase.get_comparison_choices,
                        max_length=20,
                    ),
                ),
                (
                    "flex_field_classification",
                    models.CharField(
                        choices=hope.apps.targeting.choices.FlexFieldClassification.get_choices,
                        default="NOT_FLEX_FIELD",
                        max_length=20,
                    ),
                ),
                ("field_name", models.CharField(max_length=50)),
                (
                    "arguments",
                    models.JSONField(help_text="\n                Array of arguments\n                "),
                ),
                ("round_number", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "individuals_filters_block",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="individual_block_filters",
                        to="targeting.targetingindividualrulefilterblock",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
            bases=(
                models.Model,
                hope.apps.targeting.services.targeting_service.TargetingCriteriaFilterBase,
            ),
        ),
        migrations.AddIndex(
            model_name="targetingcriteriarule",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="targeting_targetingcriteriarule_created_at_2ca50d1d",
            ),
        ),
        migrations.AddIndex(
            model_name="targetingcriteriarule",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="targeting_targetingcriteriarule_updated_at_e3aeeb64",
            ),
        ),
        migrations.AddIndex(
            model_name="targetingcriteriarulefilter",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="targeting_targetingcriteriarulefilter_created_at_81cdab54",
            ),
        ),
        migrations.AddIndex(
            model_name="targetingcriteriarulefilter",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="targeting_targetingcriteriarulefilter_updated_at_afcc44e7",
            ),
        ),
        migrations.AddIndex(
            model_name="targetingindividualrulefilterblock",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="targeting_targetingindivid_created_at_d8642e03",
            ),
        ),
        migrations.AddIndex(
            model_name="targetingindividualrulefilterblock",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="targeting_targetingindivid_updated_at_7593c42a",
            ),
        ),
        migrations.AddIndex(
            model_name="targetingindividualblockrulefilter",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="targeting_targetingindivid_created_at_c6ea6f6a",
            ),
        ),
        migrations.AddIndex(
            model_name="targetingindividualblockrulefilter",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="targeting_targetingindivid_updated_at_c9793a5c",
            ),
        ),
    ]
