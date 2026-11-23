import uuid

import concurrency.fields
from django.conf import settings
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import encrypted_fields.fields
import model_utils.fields
import timezone_field.fields

import hope.apps.core.upload_paths
import hope.models.data_collecting_type
import hope.models.flexible_attribute
import hope.models.storage_file
import hope.models.xlsx_kobo_template


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("core", "0002_migration"),
        ("core", "0003_migration"),
        ("core", "0004_migration"),
        ("core", "0005_migration"),
        ("core", "0006_migration"),
        ("core", "0007_migration"),
        ("core", "0008_migration"),
        ("core", "0009_migration"),
        ("core", "0010_migration"),
        ("core", "0011_migration"),
        ("core", "0012_migration"),
        ("core", "0013_migration"),
        ("core", "0014_migration"),
        ("core", "0015_migration"),
        ("core", "0016_migration"),
        ("core", "0017_migration"),
        ("core", "0018_migration"),
        ("core", "0019_migration"),
        ("core", "0020_migration"),
        ("core", "0021_migration"),
        ("core", "0022_migration"),
        ("core", "0023_migrate_constance_from_redis"),
        ("core", "0024_migration"),
        ("core", "0025_migration"),
        ("core", "0026_migration"),
        ("core", "0027_migration"),
        ("core", "0028_migration"),
        ("core", "0029_migration"),
        ("core", "0030_migration"),
        ("core", "0031_migration"),
        ("core", "0032_migration"),
        ("core", "0033_migration"),
        ("core", "0034_migration"),
        ("core", "0035_migration"),
        ("core", "0036_migration"),
        ("core", "0037_migration"),
        ("core", "0038_migration"),
        ("core", "0039_migration"),
        ("core", "0040_migration"),
        ("core", "0041_migration"),
        ("core", "0042_migration"),
        ("core", "0043_migration"),
    ]

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BusinessArea",
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
                ("code", models.CharField(max_length=10, unique=True)),
                ("slug", models.CharField(max_length=250, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("long_name", models.CharField(max_length=255)),
                (
                    "timezone",
                    timezone_field.fields.TimeZoneField(
                        blank=True,
                        help_text="Operational IANA timezone. When omitted, it is initialized from the office country or UTC.",
                    ),
                ),
                ("is_split", models.BooleanField(default=False)),
                ("region_code", models.CharField(max_length=8)),
                ("region_name", models.CharField(max_length=8)),
                ("has_data_sharing_agreement", models.BooleanField(default=False)),
                ("is_accountability_applicable", models.BooleanField(default=False)),
                ("rdi_import_xlsx_disabled", models.BooleanField(default=False)),
                ("active", models.BooleanField(default=False)),
                (
                    "enable_email_notification",
                    models.BooleanField(
                        default=True,
                        verbose_name="Automatic Email notifications enabled",
                    ),
                ),
                ("vision_integration_active", models.BooleanField(default=False)),
                ("rapid_pro_host", models.URLField(blank=True, null=True)),
                (
                    "rapid_pro_payment_verification_token",
                    models.CharField(blank=True, max_length=40, null=True),
                ),
                (
                    "rapid_pro_messages_token",
                    models.CharField(blank=True, max_length=40, null=True),
                ),
                (
                    "rapid_pro_survey_token",
                    models.CharField(blank=True, max_length=40, null=True),
                ),
                ("postpone_deduplication", models.BooleanField(default=False)),
                (
                    "ingest_source",
                    models.CharField(
                        choices=[
                            ("COUNTRY_WORKSPACE_ONLY", "Country Workspace only"),
                            (
                                "ALL_EXCEPT_COUNTRY_WORKSPACE",
                                "All except Country Workspace",
                            ),
                        ],
                        default="ALL_EXCEPT_COUNTRY_WORKSPACE",
                        max_length=64,
                    ),
                ),
                (
                    "deduplication_duplicate_score",
                    models.FloatField(
                        default=6.0,
                        help_text="Results equal or above this score are considered duplicates",
                        validators=[django.core.validators.MinValueValidator(0.0)],
                    ),
                ),
                (
                    "deduplication_possible_duplicate_score",
                    models.FloatField(
                        default=6.0,
                        help_text="Results equal or above this score are considered possible duplicates (needs adjudication) must be lower than deduplication_duplicate_score",
                        validators=[django.core.validators.MinValueValidator(0.0)],
                    ),
                ),
                (
                    "deduplication_batch_duplicates_percentage",
                    models.IntegerField(
                        default=50,
                        help_text="If percentage of duplicates is higher or equal to this setting, deduplication is aborted",
                    ),
                ),
                (
                    "deduplication_batch_duplicates_allowed",
                    models.IntegerField(
                        default=5,
                        help_text="If amount of duplicates for single individual exceeds this limit deduplication is aborted",
                    ),
                ),
                (
                    "deduplication_golden_record_duplicates_percentage",
                    models.IntegerField(
                        default=50,
                        help_text="If percentage of duplicates is higher or equal to this setting, deduplication is aborted",
                    ),
                ),
                (
                    "deduplication_golden_record_duplicates_allowed",
                    models.IntegerField(
                        default=5,
                        help_text="If amount of duplicates for single individual exceeds this limit deduplication is aborted",
                    ),
                ),
                ("deduplication_ignore_withdraw", models.BooleanField(default=False)),
                (
                    "biometric_deduplication_threshold",
                    models.FloatField(
                        default=0.0,
                        help_text="Threshold for Face Image Deduplication",
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(100.0),
                        ],
                    ),
                ),
                ("custom_fields", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ["name"],
                "permissions": (
                    ("can_split", "Can split BusinessArea"),
                    ("ping_rapidpro", "Can test RapidPRO connection"),
                    ("execute_sync_rapid_pro", "Can execute RapidPRO sync"),
                    ("mark_submissions", "Can mark submissions"),
                    ("reset_sync_date", "Can reset sync date"),
                ),
            },
        ),
        migrations.CreateModel(
            name="CountryCodeMap",
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
                ("ca_code", models.CharField(max_length=5, unique=True)),
            ],
            options={
                "ordering": ("country",),
            },
        ),
        migrations.CreateModel(
            name="Currency",
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
                    "code",
                    models.CharField(
                        help_text="The currency code following the ISO 4217 standard (e.g. USD, EUR)",
                        max_length=5,
                    ),
                ),
                (
                    "name",
                    models.CharField(help_text="The full name of the currency", max_length=255),
                ),
                (
                    "is_crypto",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this is a cryptocurrency (e.g. USDC)",
                    ),
                ),
                (
                    "vision_code",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="The vision system code for this currency",
                        max_length=5,
                    ),
                ),
                (
                    "active",
                    models.BooleanField(default=True, help_text="Whether this currency is active"),
                ),
                (
                    "number_of_decimals",
                    models.SmallIntegerField(
                        default=2,
                        help_text="Number of decimal places for this currency",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "currencies",
                "ordering": ["code", "vision_code"],
            },
        ),
        migrations.CreateModel(
            name="DataCollectingType",
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
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                ("code", models.CharField(max_length=32)),
                ("label", models.CharField(blank=True, max_length=32)),
                (
                    "type",
                    models.CharField(
                        blank=True,
                        choices=hope.models.data_collecting_type.DataCollectingType.Type.get_choices,
                        max_length=32,
                        null=True,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("active", models.BooleanField(default=True)),
                (
                    "deprecated",
                    models.BooleanField(
                        default=False,
                        help_text="Cannot be used in new programs, totally hidden in UI, only admin have access",
                    ),
                ),
                ("individual_filters_available", models.BooleanField(default=False)),
                ("household_filters_available", models.BooleanField(default=True)),
                (
                    "recalculate_composition",
                    models.BooleanField(
                        default=False,
                        help_text="When enabled, household composition counters (age/gender disaggregation, size, children counts) are automatically recalculated from linked individuals data",
                    ),
                ),
                (
                    "collects_individual_data",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this data collecting type registers individual members data; when enabled, known affected beneficiaries may be derived by counting linked individuals",
                    ),
                ),
                (
                    "weight",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="Ordering weight: types with a higher weight are listed first",
                    ),
                ),
            ],
            options={
                "ordering": ("-weight",),
            },
        ),
        migrations.CreateModel(
            name="FileTemp",
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
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                ("object_id", models.CharField(blank=True, max_length=120, null=True)),
                (
                    "file",
                    models.FileField(
                        max_length=255,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                ("was_downloaded", models.BooleanField(default=False)),
                (
                    "password",
                    encrypted_fields.fields.EncryptedTextField(blank=True, max_length=255, null=True),
                ),
                (
                    "xlsx_password",
                    encrypted_fields.fields.EncryptedTextField(blank=True, max_length=255, null=True),
                ),
                ("extras", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="FlexibleAttribute",
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
                ("name", models.CharField(max_length=255)),
                (
                    "type",
                    models.CharField(
                        choices=hope.models.flexible_attribute.get_type_choice_choices,
                        max_length=16,
                    ),
                ),
                (
                    "associated_with",
                    models.SmallIntegerField(choices=hope.models.flexible_attribute.get_associated_with_choices),
                ),
                ("required", models.BooleanField(default=False)),
                (
                    "label",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        validators=[hope.models.flexible_attribute.label_contains_english_en_validator],
                    ),
                ),
                ("hint", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="FlexibleAttributeChoice",
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
                ("list_name", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=255)),
                ("label", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="FlexibleAttributeGroup",
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
                ("is_removed", models.BooleanField(default=False)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("label", models.JSONField(blank=True, default=dict)),
                ("required", models.BooleanField(default=False)),
                ("repeatable", models.BooleanField(default=False)),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="PayeeType",
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
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "gl_code",
                    models.CharField(
                        blank=True,
                        help_text="General Ledger code shown on the Program",
                        max_length=32,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text="Inactive Payee Types cannot be used in new programs",
                    ),
                ),
                (
                    "weight",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="Ordering weight: types with a higher weight are listed first",
                    ),
                ),
            ],
            options={
                "verbose_name": "Payee Type",
                "verbose_name_plural": "Payee Types",
                "ordering": ("-weight", "name"),
            },
        ),
        migrations.CreateModel(
            name="PeriodicAsyncJob",
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
                    "description",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "curr_async_result_id",
                    models.CharField(
                        blank=True,
                        editable=False,
                        help_text="Current (active) AsyncResult is",
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "last_async_result_id",
                    models.CharField(
                        blank=True,
                        editable=False,
                        help_text="Latest executed AsyncResult is",
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "datetime_created",
                    models.DateTimeField(auto_now_add=True, help_text="Creation date and time"),
                ),
                (
                    "datetime_queued",
                    models.DateTimeField(
                        blank=True,
                        help_text="Queueing date and time",
                        null=True,
                        verbose_name="Queued At",
                    ),
                ),
                (
                    "repeatable",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        help_text="Indicate if the job can be repeated as-is",
                    ),
                ),
                (
                    "celery_history",
                    models.JSONField(blank=True, default=dict, editable=False),
                ),
                (
                    "local_status",
                    models.CharField(
                        blank=True,
                        default="",
                        editable=False,
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "group_key",
                    models.CharField(
                        blank=True,
                        editable=False,
                        help_text="Tasks with the same group key will not run in parallel",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("STANDARD_TASK", "Standard Task"),
                            ("JOB_TASK", "Job Task"),
                        ],
                        max_length=50,
                    ),
                ),
                ("config", models.JSONField(blank=True, default=dict)),
                ("action", models.CharField(blank=True, max_length=500, null=True)),
                ("sentry_id", models.CharField(blank=True, max_length=255, null=True)),
                ("object_id", models.CharField(blank=True, max_length=64, null=True)),
                ("job_name", models.CharField(blank=True, max_length=255, null=True)),
                ("errors", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "verbose_name": "Periodic Asynchronous Job",
                "verbose_name_plural": "Periodic Asynchronous Jobs",
            },
        ),
        migrations.CreateModel(
            name="PeriodicFieldData",
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
                    "subtype",
                    models.CharField(
                        choices=hope.models.flexible_attribute.get_periodic_type_choices,
                        max_length=16,
                    ),
                ),
                (
                    "rounds_names",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(blank=True, max_length=255),
                        default=list,
                        size=None,
                    ),
                ),
                ("number_of_rounds", models.IntegerField()),
            ],
            options={
                "verbose_name": "Periodic Field Data",
                "verbose_name_plural": "Periodic Fields Data",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="StorageFile",
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
                (
                    "file",
                    models.FileField(
                        max_length=255,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.storage_file.get_storage_status_choices,
                        default="Not processed",
                        max_length=25,
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="XLSXKoboTemplate",
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
                ("file_name", models.CharField(max_length=255)),
                (
                    "file",
                    models.FileField(
                        max_length=255,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                ("error_description", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.xlsx_kobo_template.get_kobo_status_choices,
                        max_length=200,
                    ),
                ),
                ("template_id", models.CharField(blank=True, max_length=200)),
                (
                    "first_connection_failed_time",
                    models.DateTimeField(blank=True, null=True),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "permissions": (
                    (
                        "download_last_valid_file",
                        "Can download the last valid KOBO template",
                    ),
                    ("rerun_kobo_import", "Can rerun a KOBO import"),
                ),
            },
        ),
        migrations.CreateModel(
            name="AsyncJob",
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
                    "description",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "curr_async_result_id",
                    models.CharField(
                        blank=True,
                        editable=False,
                        help_text="Current (active) AsyncResult is",
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "last_async_result_id",
                    models.CharField(
                        blank=True,
                        editable=False,
                        help_text="Latest executed AsyncResult is",
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "datetime_created",
                    models.DateTimeField(auto_now_add=True, help_text="Creation date and time"),
                ),
                (
                    "datetime_queued",
                    models.DateTimeField(
                        blank=True,
                        help_text="Queueing date and time",
                        null=True,
                        verbose_name="Queued At",
                    ),
                ),
                (
                    "repeatable",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        help_text="Indicate if the job can be repeated as-is",
                    ),
                ),
                (
                    "celery_history",
                    models.JSONField(blank=True, default=dict, editable=False),
                ),
                (
                    "local_status",
                    models.CharField(
                        blank=True,
                        default="",
                        editable=False,
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "group_key",
                    models.CharField(
                        blank=True,
                        editable=False,
                        help_text="Tasks with the same group key will not run in parallel",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("STANDARD_TASK", "Standard Task"),
                            ("JOB_TASK", "Job Task"),
                        ],
                        max_length=50,
                    ),
                ),
                ("config", models.JSONField(blank=True, default=dict)),
                ("action", models.CharField(blank=True, max_length=500, null=True)),
                ("sentry_id", models.CharField(blank=True, max_length=255, null=True)),
                ("object_id", models.CharField(blank=True, max_length=64, null=True)),
                ("job_name", models.CharField(blank=True, max_length=255, null=True)),
                ("errors", models.JSONField(blank=True, default=dict)),
                (
                    "content_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(app_label)s_%(class)s_jobs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Asynchronous Job",
                "verbose_name_plural": "Asynchronous Jobs",
                "permissions": (("recover_missing_async_job", "Can recover missing async jobs"),),
            },
        ),
    ]
