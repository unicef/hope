from decimal import Decimal
import uuid

import concurrency.fields
from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.ranges
import django.contrib.postgres.validators
import django.core.serializers.json
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import multiselectfield.db.fields
import psycopg.types.range

import hope.apps.core.upload_paths
import hope.apps.household.const
import hope.apps.payment.fields
import hope.apps.payment.validators
import hope.apps.targeting.services.targeting_service
import hope.models.account_attachment
import hope.models.approval
import hope.models.delivery_mechanism
import hope.models.financial_institution
import hope.models.financial_service_provider
import hope.models.financial_service_provider_xlsx_template
import hope.models.fsp_name_mapping
import hope.models.payment
import hope.models.payment_plan
import hope.models.payment_plan_split
import hope.models.payment_verification
import hope.models.payment_verification_plan
import hope.models.payment_verification_summary
import hope.models.utils
import hope.models.western_union_data
import hope.models.western_union_invoice
import hope.models.western_union_invoice_payment


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("payment", "0002_migration"),
        ("payment", "0003_migration"),
        ("payment", "0004_migration"),
        ("payment", "0005_migration"),
        ("payment", "0006_migration"),
        ("payment", "0007_migration"),
        ("payment", "0008_migration"),
        ("payment", "0009_migration"),
        ("payment", "0010_migration"),
        ("payment", "0011_migration"),
        ("payment", "0012_migration"),
        ("payment", "0013_migration"),
        ("payment", "0014_migration"),
        ("payment", "0015_migration"),
        ("payment", "0016_migration"),
        ("payment", "0017_migration"),
        ("payment", "0018_migration"),
        ("payment", "0019_migration"),
        ("payment", "0020_migration"),
        ("payment", "0021_migration"),
        ("payment", "0022_migration"),
        ("payment", "0023_migration"),
        ("payment", "0024_migration"),
        ("payment", "0025_migration"),
        ("payment", "0026_migration"),
        ("payment", "0027_migration"),
        ("payment", "0028_migration"),
        ("payment", "0029_migration"),
        ("payment", "0030_migration"),
        ("payment", "0031_migration"),
        ("payment", "0032_migration"),
        ("payment", "0033_migration"),
        ("payment", "0034_migration"),
        ("payment", "0035_migration"),
        ("payment", "0036_migration"),
        ("payment", "0037_migration"),
        ("payment", "0038_migration"),
        ("payment", "0039_migration"),
        ("payment", "0040_migration"),
        ("payment", "0041_migration"),
        ("payment", "0042_migration"),
        ("payment", "0043_migration"),
        ("payment", "0044_migration"),
        ("payment", "0045_migration"),
        ("payment", "0046_migration"),
        ("payment", "0047_migration"),
        ("payment", "0048_migration"),
        ("payment", "0049_migration"),
        ("payment", "0050_migration"),
        ("payment", "0051_migration"),
        ("payment", "0052_migration"),
        ("payment", "0053_migration"),
        ("payment", "0054_migration"),
        ("payment", "0055_migration"),
        ("payment", "0056_migration"),
        ("payment", "0057_migration"),
        ("payment", "0058_migration"),
        ("payment", "0059_migration"),
        ("payment", "0060_migration"),
        ("payment", "0061_migration"),
        ("payment", "0062_migration"),
        ("payment", "0063_migration"),
        ("payment", "0064_migration"),
        ("payment", "0065_migration"),
        ("payment", "0066_migration"),
        ("payment", "0067_migration"),
        ("payment", "0068_migration"),
        ("payment", "0069_migration"),
        ("payment", "0070_migration"),
        ("payment", "0071_migration"),
        ("payment", "0072_migration"),
        ("payment", "0073_migration"),
        ("payment", "0074_migration"),
        ("payment", "0075_migration"),
        ("payment", "0076_migration"),
        ("payment", "0077_migration"),
        ("payment", "0078_migration"),
        ("payment", "0079_migration"),
        ("payment", "0080_migration"),
        ("payment", "0081_migration"),
        ("payment", "0082_migration"),
        ("payment", "0083_migration"),
    ]

    dependencies = [
        ("core", "0044_baseline_models"),
        ("geo", "0010_baseline_models"),
        ("household", "0056_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountType",
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
                ("key", models.CharField(max_length=255, unique=True)),
                ("label", models.CharField(max_length=255)),
                (
                    "unique_fields",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "payment_gateway_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="FspNameMapping",
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
                ("external_name", models.CharField(max_length=255)),
                ("hope_name", models.CharField(max_length=255)),
                (
                    "source",
                    models.CharField(
                        choices=hope.models.fsp_name_mapping.FspNameMapping.SourceModel.get_choices,
                        default="Account",
                        max_length=30,
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="FspXlsxTemplatePerDeliveryMechanism",
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
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("is_removed", models.BooleanField(default=False)),
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
                    "signature_hash",
                    models.CharField(blank=True, editable=False, max_length=40),
                ),
                ("internal_data", models.JSONField(blank=True, default=dict)),
                (
                    "collector_type",
                    models.CharField(
                        choices=hope.apps.household.const.get_role_choices,
                        default="PRIMARY",
                        help_text="Collector type using for payment, by default is Primary",
                        max_length=120,
                    ),
                ),
                ("is_follow_up", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.payment.get_payment_status_choices,
                        default="Pending",
                        max_length=255,
                    ),
                ),
                ("status_date", models.DateTimeField()),
                (
                    "entitlement_quantity",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                (
                    "entitlement_quantity_usd",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                ("entitlement_date", models.DateTimeField(blank=True, null=True)),
                (
                    "delivered_quantity",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                (
                    "delivered_quantity_usd",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                ("delivery_date", models.DateTimeField(blank=True, null=True)),
                (
                    "transaction_reference_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "transaction_status_blockchain_link",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("conflicted", models.BooleanField(default=False)),
                ("excluded", models.BooleanField(default=False)),
                ("has_valid_wallet", models.BooleanField(default=True)),
                (
                    "reason_for_unsuccessful_payment",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "order_number",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(100000000),
                            django.core.validators.MaxValueValidator(999999999),
                            hope.apps.payment.validators.payment_token_and_order_number_validator,
                        ],
                    ),
                ),
                (
                    "token_number",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1000000),
                            django.core.validators.MaxValueValidator(9999999),
                            hope.apps.payment.validators.payment_token_and_order_number_validator,
                        ],
                    ),
                ),
                (
                    "additional_collector_name",
                    models.CharField(
                        blank=True,
                        help_text="Use this field for reconciliation data when funds are collected by someone other than the designated collector or the alternate collector",
                        max_length=64,
                        null=True,
                    ),
                ),
                (
                    "additional_document_type",
                    models.CharField(
                        blank=True,
                        help_text="Use this field for reconciliation data",
                        max_length=128,
                        null=True,
                    ),
                ),
                (
                    "additional_document_number",
                    models.CharField(
                        blank=True,
                        help_text="Use this field for reconciliation data",
                        max_length=128,
                        null=True,
                    ),
                ),
                (
                    "fsp_auth_code",
                    models.CharField(blank=True, help_text="FSP Auth Code", max_length=128, null=True),
                ),
                ("extras", models.JSONField(blank=True, default=dict)),
                (
                    "vulnerability_score",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        help_text="Written by Steficon",
                        max_digits=6,
                        null=True,
                    ),
                ),
                ("is_cash_assist", models.BooleanField(default=False)),
                (
                    "sent_to_fsp_date",
                    models.DateTimeField(blank=True, help_text="Sent to FSP on date", null=True),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "permissions": (
                    (
                        "pm_sync_payment_with_pg",
                        "Can sync payment with payment gateway",
                    ),
                ),
            },
            bases=(hope.models.utils.AdminUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name="PaymentHouseholdSnapshot",
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
                ("snapshot_data", models.JSONField(blank=True, default=dict)),
                ("household_id", models.UUIDField()),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="PaymentPlan",
            fields=[
                ("is_removed", models.BooleanField(default=False)),
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
                    "version",
                    concurrency.fields.IntegerVersionField(default=0, help_text="record revision number"),
                ),
                ("unicef_id", models.CharField(blank=True, max_length=255, null=True)),
                ("internal_data", models.JSONField(blank=True, default=dict)),
                (
                    "closure_comment",
                    models.TextField(
                        blank=True,
                        help_text="Justification comment provided at closure",
                        null=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        help_text="Name",
                        max_length=255,
                        null=True,
                        validators=[
                            django.core.validators.MinLengthValidator(3),
                            django.core.validators.MaxLengthValidator(255),
                            django.core.validators.RegexValidator(
                                "\\s{2,}",
                                "Double spaces characters are not allowed.",
                                code="double_spaces_characters_not_allowed",
                                inverse_match=True,
                            ),
                            django.core.validators.RegexValidator(
                                "(^\\s+)|(\\s+$)",
                                "Leading or trailing spaces characters are not allowed.",
                                code="leading_trailing_spaces_characters_not_allowed",
                                inverse_match=True,
                            ),
                            django.core.validators.ProhibitNullCharactersValidator(),
                        ],
                    ),
                ),
                (
                    "start_date",
                    models.DateTimeField(blank=True, help_text="Payment Plan start date", null=True),
                ),
                (
                    "end_date",
                    models.DateTimeField(blank=True, help_text="Payment Plan end date", null=True),
                ),
                (
                    "dispersion_start_date",
                    models.DateField(blank=True, help_text="Dispersion Start Date", null=True),
                ),
                (
                    "dispersion_end_date",
                    models.DateField(blank=True, help_text="Dispersion End Date", null=True),
                ),
                (
                    "excluded_ids",
                    models.TextField(blank=True, help_text="Targeting level exclusion IDs", null=True),
                ),
                (
                    "exclusion_reason",
                    models.TextField(
                        blank=True,
                        help_text="Exclusion reason (Targeting level)",
                        null=True,
                    ),
                ),
                (
                    "vulnerability_score_min",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        help_text="Written by a tool such as Engine Formula",
                        max_digits=6,
                        null=True,
                    ),
                ),
                (
                    "vulnerability_score_max",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        help_text="Written by a tool such as Engine Formula",
                        max_digits=6,
                        null=True,
                    ),
                ),
                (
                    "abort_comment",
                    models.CharField(blank=True, help_text="Reason for aborting", max_length=2000),
                ),
                (
                    "flat_amount_value",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Apply a fixed amount of entitlement for all payment records within a payment plan",
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.payment_plan.PaymentPlan.Status.get_choices,
                        default="TP_OPEN",
                        help_text="Status [sys]",
                        max_length=50,
                    ),
                ),
                (
                    "background_action_status",
                    models.CharField(
                        blank=True,
                        choices=hope.models.payment_plan.PaymentPlan.BackgroundActionStatus.get_choices,
                        default=None,
                        help_text="Background Action Status for celery task [sys]",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "build_status",
                    models.CharField(
                        blank=True,
                        choices=hope.models.payment_plan.PaymentPlan.BuildStatus.get_choices,
                        default=None,
                        help_text="Build Status for celery task [sys]",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "built_at",
                    models.DateTimeField(blank=True, help_text="Built at [sys]", null=True),
                ),
                (
                    "exchange_rate",
                    models.DecimalField(
                        blank=True,
                        decimal_places=8,
                        help_text="Exchange Rate [sys]",
                        max_digits=15,
                        null=True,
                    ),
                ),
                (
                    "custom_exchange_rate",
                    models.BooleanField(default=False, help_text="Custom Exchange Rate flag [sys]"),
                ),
                (
                    "use_payment_gateway",
                    models.BooleanField(
                        default=False,
                        help_text="Send this payment plan through the payment gateway regardless of the FSP communication channel",
                    ),
                ),
                (
                    "female_children_count",
                    models.PositiveIntegerField(default=0, help_text="Female Children Count [sys]"),
                ),
                (
                    "male_children_count",
                    models.PositiveIntegerField(default=0, help_text="Male Children Count [sys]"),
                ),
                (
                    "female_adults_count",
                    models.PositiveIntegerField(default=0, help_text="Female Adults Count [sys]"),
                ),
                (
                    "male_adults_count",
                    models.PositiveIntegerField(default=0, help_text="Male Adults Count [sys]"),
                ),
                (
                    "total_households_count",
                    models.PositiveIntegerField(default=0, help_text="Total Households Count [sys]"),
                ),
                (
                    "total_individuals_count",
                    models.PositiveIntegerField(default=0, help_text="Total Individuals Count [sys]"),
                ),
                (
                    "imported_file_date",
                    models.DateTimeField(blank=True, help_text="Imported File Date [sys]", null=True),
                ),
                (
                    "total_entitled_quantity",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total Entitled Quantity [sys]",
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal(0))],
                    ),
                ),
                (
                    "total_entitled_quantity_usd",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total Entitled Quantity USD [sys]",
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal(0))],
                    ),
                ),
                (
                    "total_entitled_quantity_revised",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total Entitled Quantity Revised [sys]",
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal(0))],
                    ),
                ),
                (
                    "total_entitled_quantity_revised_usd",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total Entitled Quantity Revised USD [sys]",
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal(0))],
                    ),
                ),
                (
                    "total_delivered_quantity",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total Delivered Quantity [sys]",
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal(0))],
                    ),
                ),
                (
                    "total_delivered_quantity_usd",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total Delivered Quantity USD [sys]",
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal(0))],
                    ),
                ),
                (
                    "total_undelivered_quantity",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total Undelivered Quantity [sys]",
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal(0))],
                    ),
                ),
                (
                    "total_undelivered_quantity_usd",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total Undelivered Quantity USD [sys]",
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal(0))],
                    ),
                ),
                (
                    "steficon_targeting_applied_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="Engine Formula applied date for targeting [sys]",
                        null=True,
                    ),
                ),
                (
                    "steficon_applied_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="Engine Formula applied date [sys]",
                        null=True,
                    ),
                ),
                (
                    "plan_type",
                    models.CharField(
                        choices=[
                            ("REGULAR", "Regular"),
                            ("TOP_UP", "Top Up"),
                            ("FOLLOW_UP", "Follow Up"),
                            ("TOP_UP_AMENDMENT", "Top Up Amendment"),
                        ],
                        default="REGULAR",
                        help_text="Payment Plan type [sys]",
                        max_length=20,
                    ),
                ),
                (
                    "export_tag",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        help_text="Group delivery export batch number; set when the plan is included in a group export [sys]",
                        null=True,
                    ),
                ),
                (
                    "exclude_household_error",
                    models.TextField(
                        blank=True,
                        help_text="Exclusion reason (Targeting level) [sys]",
                        null=True,
                    ),
                ),
                (
                    "status_date",
                    models.DateTimeField(help_text="Date and time of Payment Plan status [sys]"),
                ),
                (
                    "is_cash_assist",
                    models.BooleanField(default=False, help_text="Cash Assist Flag [sys]"),
                ),
                (
                    "flag_exclude_if_active_adjudication_ticket",
                    models.BooleanField(
                        default=False,
                        help_text="Exclude households with individuals (members or collectors) that have active adjudication ticket(s).",
                    ),
                ),
                (
                    "flag_exclude_if_on_sanction_list",
                    models.BooleanField(
                        default=False,
                        help_text="Exclude households with individuals (members or collectors) on sanction list.",
                    ),
                ),
            ],
            options={
                "verbose_name": "Payment Plan",
                "ordering": ["created_at"],
                "permissions": (
                    (
                        "recalculate_exchange_rate",
                        "Can recalculate USD values based on exchange rate",
                    ),
                    (
                        "restart_preparing_payment_plan",
                        "Can restart Preparing Payment Plans",
                    ),
                    (
                        "restart_exporting_template_for_entitlement",
                        "Can restart Exporting Template for Entitlements",
                    ),
                    (
                        "restart_exporting_payment_plan_list",
                        "Can restart Exporting Payment Plans",
                    ),
                    (
                        "restart_importing_reconciliation_xlsx_file",
                        "Can restart Importing Reconciliation XLSX File",
                    ),
                    (
                        "pm_sync_payment_plan_with_pg",
                        "Can sync payment plan with payment gateway",
                    ),
                    (
                        "pm_manage_vision_workflow",
                        "Can manage Payment Plan Vision workflow",
                    ),
                    (
                        "download_payment_instruction",
                        "Can download payment instruction from payment gateway",
                    ),
                ),
            },
            bases=(
                models.Model,
                hope.models.utils.AdminUrlMixin,
                hope.apps.targeting.services.targeting_service.TargetingCriteriaQueryingBase,
            ),
        ),
        migrations.CreateModel(
            name="PaymentPlanGroup",
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
                ("name", models.CharField(default="Default Group", max_length=255)),
                (
                    "background_action_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("XLSX_EXPORTING", "Exporting XLSX file"),
                            ("XLSX_EXPORT_ERROR", "Export XLSX file Error"),
                            (
                                "XLSX_IMPORTING_RECONCILIATION",
                                "Importing Reconciliation XLSX file",
                            ),
                            ("XLSX_IMPORT_ERROR", "Import XLSX file Error"),
                        ],
                        default=None,
                        help_text="Background Action Status for celery export/import task [sys]",
                        max_length=50,
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Payment Plan Group",
                "ordering": ["created_at"],
            },
            bases=(models.Model, hope.models.utils.AdminUrlMixin),
        ),
        migrations.CreateModel(
            name="PaymentPlanPurpose",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Payment Plan Purpose",
            },
        ),
        migrations.CreateModel(
            name="PaymentPlanSplit",
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
                    "split_type",
                    models.CharField(
                        choices=hope.models.payment_plan_split.PaymentPlanSplit.SplitType.get_choices,
                        default="NO_SPLIT",
                        max_length=24,
                    ),
                ),
                ("chunks_no", models.IntegerField(blank=True, null=True)),
                ("sent_to_payment_gateway", models.BooleanField(default=False)),
                ("order", models.IntegerField(default=0)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="PaymentPlanSplitPayments",
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
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="PaymentPlanSupportingDocument",
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
                ("title", models.CharField(max_length=255)),
                (
                    "file",
                    models.FileField(
                        max_length=255,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["uploaded_at"],
            },
        ),
        migrations.CreateModel(
            name="PaymentVerification",
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
                    "version",
                    concurrency.fields.IntegerVersionField(default=0, help_text="record revision number"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.payment_verification.get_status_choices,
                        default="PENDING",
                        max_length=50,
                    ),
                ),
                ("status_date", models.DateTimeField(blank=True, null=True)),
                (
                    "received_amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                ("sent_to_rapid_pro", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ("id",),
            },
            bases=(models.Model, hope.models.utils.AdminUrlMixin),
        ),
        migrations.CreateModel(
            name="PaymentVerificationPlan",
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
                    "version",
                    concurrency.fields.IntegerVersionField(default=0, help_text="record revision number"),
                ),
                ("unicef_id", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.payment_verification_plan.get_status_choices,
                        default="PENDING",
                        max_length=50,
                    ),
                ),
                (
                    "verification_channel",
                    models.CharField(
                        choices=hope.models.payment_verification_plan.get_verification_channel_choices,
                        max_length=50,
                    ),
                ),
                (
                    "sampling",
                    models.CharField(
                        choices=hope.models.payment_verification_plan.get_sampling_choices,
                        max_length=50,
                    ),
                ),
                ("sex_filter", models.CharField(blank=True, max_length=10, null=True)),
                ("activation_date", models.DateTimeField(blank=True, null=True)),
                ("completion_date", models.DateTimeField(blank=True, null=True)),
                ("sample_size", models.PositiveIntegerField(blank=True, null=True)),
                ("responded_count", models.PositiveIntegerField(blank=True, null=True)),
                ("received_count", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "not_received_count",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "received_with_problems_count",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("confidence_interval", models.FloatField(blank=True, null=True)),
                ("margin_of_error", models.FloatField(blank=True, null=True)),
                ("rapid_pro_flow_id", models.CharField(blank=True, max_length=255)),
                (
                    "rapid_pro_flow_start_uuids",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(blank=True, max_length=255),
                        default=list,
                        size=None,
                    ),
                ),
                ("xlsx_file_exporting", models.BooleanField(default=False)),
                ("xlsx_file_imported", models.BooleanField(default=False)),
                ("error", models.CharField(blank=True, max_length=500, null=True)),
                ("age_filter", models.JSONField(blank=True, null=True)),
                (
                    "excluded_admin_areas_filter",
                    models.JSONField(blank=True, null=True),
                ),
            ],
            options={
                "ordering": ("created_at",),
            },
            bases=(models.Model, hope.models.utils.AdminUrlMixin),
        ),
        migrations.CreateModel(
            name="PaymentVerificationSummary",
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
                    "status",
                    models.CharField(
                        choices=hope.models.payment_verification_summary.get_status_choices,
                        default="PENDING",
                        max_length=50,
                        verbose_name="Verification status",
                    ),
                ),
                ("activation_date", models.DateTimeField(blank=True, null=True)),
                ("completion_date", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="WesternUnionData",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("date", models.DateField(blank=True, null=True)),
                (
                    "amount",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.western_union_data.get_status_choices,
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("error_msg", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Western Union Data",
                "verbose_name_plural": "Western Union Data",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="WesternUnionInvoice",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("is_legacy", models.BooleanField(default=False)),
                ("date", models.DateField(blank=True, null=True)),
                (
                    "advice_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "net_amount",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "charges",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.western_union_invoice.get_status_choices,
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("error_msg", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Western Union Invoice",
                "verbose_name_plural": "Western Union Invoices",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="WesternUnionInvoicePayment",
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
                    "transaction_status",
                    models.CharField(
                        blank=True,
                        choices=hope.models.western_union_invoice_payment.get_transaction_status_choices,
                        max_length=1,
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="WesternUnionPaymentPlanReport",
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
                ("sent", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Western Union Payment Plan Report",
                "verbose_name_plural": "Western Union Payment Plan Reports",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="AcceptanceProcessThreshold",
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
                    "payments_range_usd",
                    django.contrib.postgres.fields.ranges.IntegerRangeField(
                        default=psycopg.types.range.Range(0, None, "[)"),
                        validators=[django.contrib.postgres.validators.RangeMinValueValidator(0)],
                    ),
                ),
                ("approval_number_required", models.PositiveIntegerField(default=1)),
                (
                    "authorization_number_required",
                    models.PositiveIntegerField(default=1),
                ),
                (
                    "finance_release_number_required",
                    models.PositiveIntegerField(default=1),
                ),
                (
                    "business_area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="acceptance_process_thresholds",
                        to="core.businessarea",
                    ),
                ),
            ],
            options={
                "ordering": ("payments_range_usd",),
            },
        ),
        migrations.CreateModel(
            name="Account",
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
                (
                    "rdi_merge_status",
                    models.CharField(
                        blank=True,
                        choices=hope.models.utils.get_merge_status_choices,
                        default="PENDING",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "signature_hash",
                    models.CharField(blank=True, editable=False, max_length=40),
                ),
                (
                    "number",
                    models.CharField(
                        blank=True,
                        help_text="The account number or wallet identifier",
                        max_length=256,
                        null=True,
                    ),
                ),
                (
                    "data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                        help_text="Additional account-specific fields",
                    ),
                ),
                (
                    "unique_key",
                    models.CharField(blank=True, editable=False, max_length=256, null=True),
                ),
                ("is_unique", models.BooleanField(default=True)),
                ("active", models.BooleanField(default=True)),
                (
                    "individual",
                    models.ForeignKey(
                        help_text="The individual this account belongs to",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accounts",
                        to="household.individual",
                    ),
                ),
                (
                    "account_type",
                    models.ForeignKey(
                        help_text="The type of account (e.g. bank, wallet)",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="payment.accounttype",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="PaymentDataCollector",
            fields=[],
            options={
                "verbose_name": "Payment Data Collector",
                "verbose_name_plural": "Payment Data Collectors",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("payment.account",),
        ),
        migrations.CreateModel(
            name="PendingAccount",
            fields=[],
            options={
                "verbose_name": "Imported Account",
                "verbose_name_plural": "Imported Accounts",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("payment.account",),
        ),
        migrations.CreateModel(
            name="AccountAttachment",
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
                ("title", models.CharField(blank=True, default="", max_length=255)),
                (
                    "file",
                    models.FileField(
                        max_length=500,
                        upload_to=hope.models.account_attachment.account_attachment_path,
                    ),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="payment.account",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["uploaded_at"],
            },
        ),
        migrations.CreateModel(
            name="ApprovalProcess",
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
                ("sent_for_approval_date", models.DateTimeField(blank=True, null=True)),
                (
                    "sent_for_authorization_date",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "sent_for_finance_release_date",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("approval_number_required", models.PositiveIntegerField(default=1)),
                (
                    "authorization_number_required",
                    models.PositiveIntegerField(default=1),
                ),
                (
                    "finance_release_number_required",
                    models.PositiveIntegerField(default=1),
                ),
                (
                    "sent_for_approval_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sent_for_authorization_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sent_for_finance_release_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Approval Processes",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="Approval",
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
                    "type",
                    models.CharField(
                        choices=hope.models.approval.get_approval_type_choices,
                        default="APPROVAL",
                        max_length=50,
                        verbose_name="Approval type",
                    ),
                ),
                ("comment", models.CharField(blank=True, max_length=2000, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "approval_process",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approvals",
                        to="payment.approvalprocess",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="DeliveryMechanism",
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
                    "payment_gateway_id",
                    models.CharField(blank=True, max_length=255, null=True, unique=True),
                ),
                ("code", models.CharField(max_length=255, unique=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "transfer_type",
                    models.CharField(
                        choices=hope.models.delivery_mechanism.DeliveryMechanism.TransferType.get_choices,
                        default="CASH",
                        max_length=255,
                    ),
                ),
                (
                    "account_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="delivery_mechanisms",
                        to="payment.accounttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Delivery Mechanism",
                "verbose_name_plural": "Delivery Mechanisms",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="FinancialInstitution",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "type",
                    models.CharField(
                        choices=hope.models.financial_institution.FinancialInstitution.FinancialInstitutionType.get_choices,
                        max_length=30,
                    ),
                ),
                ("swift_code", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="geo.country",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.AddField(
            model_name="account",
            name="financial_institution",
            field=models.ForeignKey(
                blank=True,
                help_text="The financial institution holding this account",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="payment.financialinstitution",
            ),
        ),
        migrations.CreateModel(
            name="FinancialServiceProvider",
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
                ("internal_data", models.JSONField(blank=True, default=dict)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("vision_vendor_number", models.CharField(max_length=100, unique=True)),
                (
                    "distribution_limit",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="The maximum amount of money in USD that can be distributed or unlimited if null",
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                (
                    "communication_channel",
                    models.CharField(
                        choices=hope.models.financial_service_provider.get_communication_channel_choices,
                        max_length=6,
                    ),
                ),
                (
                    "data_transfer_configuration",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="JSON configuration for the data transfer mechanism",
                        null=True,
                    ),
                ),
                (
                    "payment_gateway_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "allowed_business_areas",
                    models.ManyToManyField(blank=True, to="core.businessarea"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_financial_service_providers",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "delivery_mechanisms",
                    models.ManyToManyField(to="payment.deliverymechanism"),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="FinancialInstitutionMapping",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=30)),
                (
                    "financial_institution",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="payment.financialinstitution",
                    ),
                ),
                (
                    "financial_service_provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="payment.financialserviceprovider",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="DeliveryMechanismConfig",
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
                    "required_fields",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="geo.country",
                    ),
                ),
                (
                    "delivery_mechanism",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="payment.deliverymechanism",
                    ),
                ),
                (
                    "fsp",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="payment.financialserviceprovider",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="FinancialServiceProviderXlsxTemplate",
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
                ("name", models.CharField(max_length=120, verbose_name="Name")),
                (
                    "columns",
                    multiselectfield.db.fields.MultiSelectField(
                        choices=hope.models.financial_service_provider_xlsx_template.get_columns_choices,
                        default=[
                            "payment_id",
                            "household_id",
                            "individual_id",
                            "household_size",
                            "collector_name",
                            "alternate_collector_full_name",
                            "alternate_collector_given_name",
                            "alternate_collector_family_name",
                            "alternate_collector_middle_name",
                            "alternate_collector_phone_no",
                            "alternate_collector_document_numbers",
                            "alternate_collector_sex",
                            "collector_type",
                            "payment_channel",
                            "fsp_name",
                            "currency",
                            "entitlement_quantity",
                            "entitlement_quantity_usd",
                            "delivered_quantity",
                            "delivery_date",
                            "reference_id",
                            "reason_for_unsuccessful_payment",
                            "order_number",
                            "token_number",
                            "additional_collector_name",
                            "additional_document_type",
                            "additional_document_number",
                            "registration_token",
                            "status",
                            "transaction_status_blockchain_link",
                            "fsp_auth_code",
                            "account_data",
                        ],
                        help_text="Select the columns to include in the report",
                        max_length=1000,
                        verbose_name="Columns",
                    ),
                ),
                (
                    "core_fields",
                    hope.apps.payment.fields.DynamicChoiceArrayField(
                        base_field=models.CharField(blank=True, max_length=255),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "flex_fields",
                    hope.models.financial_service_provider_xlsx_template.FlexFieldArrayField(
                        base_field=models.CharField(blank=True, max_length=255),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "document_types",
                    hope.apps.payment.fields.DynamicChoiceArrayField(
                        base_field=models.CharField(blank=True, max_length=255),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_financial_service_provider_xlsx_templates",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="FollowUpInstruction",
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
                    "background_action_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("XLSX_EXPORTING", "Exporting XLSX"),
                            (
                                "XLSX_IMPORTING_RECONCILIATION",
                                "Importing Reconciliation from XLSX",
                            ),
                            ("XLSX_EXPORT_ERROR", "Error while exporting XLSX"),
                            ("XLSX_IMPORT_ERROR", "Error while importing XLSX"),
                        ],
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "business_area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="core.businessarea",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_follow_up_instructions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "export_file",
                    models.ForeignKey(
                        blank=True,
                        help_text="Export File",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="core.filetemp",
                    ),
                ),
            ],
            options={
                "verbose_name": "Follow Up Instruction",
                "verbose_name_plural": "Follow Up Instructions",
                "ordering": ["created_at"],
            },
            bases=(models.Model, hope.models.utils.AdminUrlMixin),
        ),
    ]
