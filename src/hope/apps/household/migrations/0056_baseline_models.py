import uuid

import concurrency.fields
from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.search
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import multiselectfield.db.fields
import phonenumber_field.modelfields
import sorl.thumbnail.fields

import hope.apps.core.languages
import hope.apps.core.upload_paths
import hope.apps.core.utils
import hope.apps.household.const
import hope.apps.household.mixins
import hope.models.document
import hope.models.entitlement_card
import hope.models.household
import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("household", "0002_migration"),
        ("household", "0003_migration"),
        ("household", "0004_migration"),
        ("household", "0005_migration"),
        ("household", "0006_migration"),
        ("household", "0007_migration"),
        ("household", "0008_migration"),
        ("household", "0009_migration"),
        ("household", "0010_migration"),
        ("household", "0011_migration"),
        ("household", "0012_migration"),
        ("household", "0013_migration"),
        ("household", "0014_migration"),
        ("household", "0015_migration"),
        ("household", "0016_migration"),
        ("household", "0017_migration"),
        ("household", "0018_migration"),
        ("household", "0019_migration"),
        ("household", "0020_migration"),
        ("household", "0021_migration"),
        ("household", "0022_migration"),
        ("household", "0023_migration"),
        ("household", "0024_migration"),
        ("household", "0025_migration"),
        ("household", "0026_migration"),
        ("household", "0027_migration"),
        ("household", "0028_migration"),
        ("household", "0029_migration"),
        ("household", "0030_migration"),
        ("household", "0031_migration"),
        ("household", "0032_migration"),
        ("household", "0033_migration"),
        ("household", "0034_migration"),
        ("household", "0035_migration"),
        ("household", "0036_migration"),
        ("household", "0037_migration"),
        ("household", "0038_migration"),
        ("household", "0039_migration"),
        ("household", "0040_migration"),
        ("household", "0041_migration"),
        ("household", "0042_migration"),
        ("household", "0043_migration"),
        ("household", "0044_migration"),
        ("household", "0045_migration"),
        ("household", "0046_migration"),
        ("household", "0047_migration"),
        ("household", "0048_migration"),
        ("household", "0049_migration"),
        ("household", "0050_migration"),
        ("household", "0051_migration"),
        ("household", "0052_migration"),
        ("household", "0053_migration"),
        ("household", "0054_migration"),
        ("household", "0055_migration"),
    ]

    dependencies = [
        ("geo", "0010_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Collation of the db_collation fields below.
        migrations.RunSQL(
            sql="CREATE COLLATION IF NOT EXISTS \"und-ci-det\" (provider = icu, locale = 'und-u-ks-level2', deterministic = true);",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Called by a check constraint on Document.
        migrations.RunSQL(
            sql="""CREATE OR REPLACE FUNCTION check_unique_document_for_individual(uuid, boolean)
 RETURNS boolean
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
            begin
                return(select exists(select 1 from household_documenttype where id = $1 and unique_for_individual = $2));
            end;
            $function$""",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name="DocumentType",
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
                ("label", models.CharField(max_length=100)),
                ("key", models.CharField(max_length=50, unique=True)),
                ("is_identity_document", models.BooleanField(default=True)),
                ("unique_for_individual", models.BooleanField(default=False)),
                ("valid_for_deduplication", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["label"],
            },
        ),
        migrations.CreateModel(
            name="DocumentValidator",
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
                ("regex", models.CharField(default=".*", max_length=100)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="EntitlementCard",
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
                ("card_number", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.entitlement_card.get_status_choices,
                        default="ACTIVE",
                        max_length=10,
                    ),
                ),
                ("card_type", models.CharField(max_length=255)),
                ("current_card_size", models.CharField(max_length=255)),
                ("card_custodian", models.CharField(max_length=255)),
                ("service_provider", models.CharField(max_length=255)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="Facility",
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
                    "name",
                    models.CharField(help_text="Facility or Organization name", max_length=255),
                ),
            ],
            options={
                "verbose_name_plural": "Facilities",
                "ordering": ("business_area", "name"),
            },
        ),
        migrations.CreateModel(
            name="Household",
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
                ("is_removed", models.BooleanField(default=False)),
                ("removed_date", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("last_sync_at", models.DateTimeField(blank=True, null=True)),
                (
                    "version",
                    concurrency.fields.IntegerVersionField(default=0, help_text="record revision number"),
                ),
                ("unicef_id", models.CharField(blank=True, max_length=255, null=True)),
                ("internal_data", models.JSONField(blank=True, default=dict)),
                (
                    "consent_sign",
                    sorl.thumbnail.fields.ImageField(
                        blank=True,
                        help_text="Household consent sign image",
                        max_length=255,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                        validators=[django.core.validators.validate_image_file_extension],
                    ),
                ),
                (
                    "consent",
                    models.BooleanField(blank=True, help_text="Household consent", null=True),
                ),
                (
                    "consent_sharing",
                    multiselectfield.db.fields.MultiSelectField(
                        blank=True,
                        choices=hope.apps.household.const.get_data_sharing_choices,
                        default="",
                        help_text="Household consent sharing",
                        max_length=63,
                    ),
                ),
                (
                    "residence_status",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_residence_status_choices,
                        help_text="Household residence status",
                        max_length=254,
                    ),
                ),
                (
                    "address",
                    models.CharField(
                        blank=True,
                        db_collation="und-ci-det",
                        help_text="Household address",
                        max_length=1024,
                    ),
                ),
                (
                    "zip_code",
                    models.CharField(
                        blank=True,
                        help_text="Household zip code",
                        max_length=12,
                        null=True,
                    ),
                ),
                (
                    "size",
                    models.PositiveIntegerField(blank=True, help_text="Household size", null=True),
                ),
                (
                    "female_age_group_0_5_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female age group 0-5",
                        null=True,
                    ),
                ),
                (
                    "female_age_group_6_11_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female age group 6-11",
                        null=True,
                    ),
                ),
                (
                    "female_age_group_12_17_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female age group 12-17",
                        null=True,
                    ),
                ),
                (
                    "female_age_group_18_59_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female age group 18-59",
                        null=True,
                    ),
                ),
                (
                    "female_age_group_60_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female age group 60",
                        null=True,
                    ),
                ),
                (
                    "pregnant_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household pregnant count",
                        null=True,
                    ),
                ),
                (
                    "male_age_group_0_5_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male age group 0-5",
                        null=True,
                    ),
                ),
                (
                    "male_age_group_6_11_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male age group 6-11",
                        null=True,
                    ),
                ),
                (
                    "male_age_group_12_17_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male age group 12-17",
                        null=True,
                    ),
                ),
                (
                    "male_age_group_18_59_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male age group 18-59",
                        null=True,
                    ),
                ),
                (
                    "male_age_group_60_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male age group 60",
                        null=True,
                    ),
                ),
                (
                    "female_age_group_0_5_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female age group 0-5",
                        null=True,
                    ),
                ),
                (
                    "female_age_group_6_11_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female age group 6-11",
                        null=True,
                    ),
                ),
                (
                    "female_age_group_12_17_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female age group 12-17",
                        null=True,
                    ),
                ),
                (
                    "female_age_group_18_59_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female age group 18-59",
                        null=True,
                    ),
                ),
                (
                    "female_age_group_60_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female age group 60",
                        null=True,
                    ),
                ),
                (
                    "male_age_group_0_5_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male age group 0-5",
                        null=True,
                    ),
                ),
                (
                    "male_age_group_6_11_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male age group 6-1",
                        null=True,
                    ),
                ),
                (
                    "male_age_group_12_17_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male age group 12-17",
                        null=True,
                    ),
                ),
                (
                    "male_age_group_18_59_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male age group 18-59",
                        null=True,
                    ),
                ),
                (
                    "male_age_group_60_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male age group 60",
                        null=True,
                    ),
                ),
                (
                    "children_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household children count",
                        null=True,
                    ),
                ),
                (
                    "male_children_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male children count",
                        null=True,
                    ),
                ),
                (
                    "female_children_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female children count",
                        null=True,
                    ),
                ),
                (
                    "children_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household children disabled count",
                        null=True,
                    ),
                ),
                (
                    "male_children_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household male children disabled count",
                        null=True,
                    ),
                ),
                (
                    "female_children_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household female children disabled count",
                        null=True,
                    ),
                ),
                (
                    "other_sex_group_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household other sex group count",
                        null=True,
                    ),
                ),
                (
                    "unknown_sex_group_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text="Household unknown sex group count",
                        null=True,
                    ),
                ),
                (
                    "kab_female_age_group_0_5_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: females aged 0-5",
                        null=True,
                    ),
                ),
                (
                    "kab_female_age_group_6_11_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: females aged 6-11",
                        null=True,
                    ),
                ),
                (
                    "kab_female_age_group_12_17_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: females aged 12-17",
                        null=True,
                    ),
                ),
                (
                    "kab_female_age_group_18_59_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: females aged 18-59",
                        null=True,
                    ),
                ),
                (
                    "kab_female_age_group_60_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: females aged 60+",
                        null=True,
                    ),
                ),
                (
                    "kab_male_age_group_0_5_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: males aged 0-5",
                        null=True,
                    ),
                ),
                (
                    "kab_male_age_group_6_11_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: males aged 6-11",
                        null=True,
                    ),
                ),
                (
                    "kab_male_age_group_12_17_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: males aged 12-17",
                        null=True,
                    ),
                ),
                (
                    "kab_male_age_group_18_59_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: males aged 18-59",
                        null=True,
                    ),
                ),
                (
                    "kab_male_age_group_60_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: males aged 60+",
                        null=True,
                    ),
                ),
                (
                    "kab_female_age_group_0_5_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: females aged 0-5 with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_female_age_group_6_11_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: females aged 6-11 with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_female_age_group_12_17_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: females aged 12-17 with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_female_age_group_18_59_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: females aged 18-59 with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_female_age_group_60_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: females aged 60+ with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_male_age_group_0_5_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: males aged 0-5 with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_male_age_group_6_11_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: males aged 6-11 with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_male_age_group_12_17_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: males aged 12-17 with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_male_age_group_18_59_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: males aged 18-59 with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_male_age_group_60_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: males aged 60+ with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_size",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: total count",
                        null=True,
                    ),
                ),
                (
                    "kab_pregnant_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: pregnant members",
                        null=True,
                    ),
                ),
                (
                    "kab_children_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: children (under 18)",
                        null=True,
                    ),
                ),
                (
                    "kab_female_children_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: female children (under 18)",
                        null=True,
                    ),
                ),
                (
                    "kab_male_children_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: male children (under 18)",
                        null=True,
                    ),
                ),
                (
                    "kab_children_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: children (under 18) with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_female_children_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: female children (under 18) with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_male_children_disabled_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: male children (under 18) with disability",
                        null=True,
                    ),
                ),
                (
                    "kab_other_sex_group_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: members with other sex",
                        null=True,
                    ),
                ),
                (
                    "kab_unknown_sex_group_count",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Known affected beneficiaries: members with sex not collected",
                        null=True,
                    ),
                ),
                (
                    "returnee",
                    models.BooleanField(blank=True, help_text="Household returnee status", null=True),
                ),
                (
                    "fchild_hoh",
                    models.BooleanField(
                        blank=True,
                        help_text="Female child headed household flag",
                        null=True,
                    ),
                ),
                (
                    "child_hoh",
                    models.BooleanField(blank=True, help_text="Child headed household flag", null=True),
                ),
                (
                    "village",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Household village",
                        max_length=250,
                    ),
                ),
                (
                    "unhcr_id",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Household unhcr id",
                        max_length=250,
                    ),
                ),
                (
                    "detail_id",
                    models.CharField(
                        blank=True,
                        help_text="Kobo asset ID, Xlsx row ID, Aurora registration ID",
                        max_length=150,
                        null=True,
                    ),
                ),
                (
                    "originating_id",
                    models.CharField(
                        blank=True,
                        help_text="A unified external reference with a fixed-length source prefix (XLS, KOB, or AUR)\n                     and a source-specific identifier separated by '#', e.g., 'KOB#321#123'.",
                        max_length=150,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="originating_id must start with: KOB, AUR, XLS, API",
                                regex="^(KOB|AUR|XLS|API)#.+$",
                            )
                        ],
                    ),
                ),
                (
                    "start",
                    models.DateTimeField(blank=True, help_text="Data collection start date", null=True),
                ),
                (
                    "registration_method",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_registration_method_choices,
                        default="",
                        help_text="Household registration method [sys]",
                        max_length=250,
                    ),
                ),
                (
                    "family_id",
                    models.CharField(
                        blank=True,
                        help_text="Family ID eDopomoga household id [sys]",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "origin_unicef_id",
                    models.CharField(
                        blank=True,
                        help_text="Household origin unicef id [sys]",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "is_migration_handled",
                    models.BooleanField(default=False, help_text="Household migration status [sys]"),
                ),
                (
                    "migrated_at",
                    models.DateTimeField(blank=True, help_text="Household migrated at [sys]", null=True),
                ),
                (
                    "collect_type",
                    models.CharField(
                        blank=True,
                        choices=hope.models.household.Household.CollectType.get_choices,
                        default="STANDARD",
                        help_text="Household collect type [sys]",
                        max_length=8,
                    ),
                ),
                (
                    "program_registration_id",
                    models.CharField(
                        blank=True,
                        db_collation="und-ci-det",
                        help_text="Beneficiary Program Registration id [sys]",
                        max_length=100,
                        null=True,
                        unique=True,
                        verbose_name="Beneficiary Program Registration Id",
                    ),
                ),
                (
                    "total_cash_received_usd",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Household cash received usd [sys]",
                        max_digits=64,
                        null=True,
                    ),
                ),
                (
                    "total_cash_received",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Household cash received [sys]",
                        max_digits=64,
                        null=True,
                    ),
                ),
                (
                    "flex_fields",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Household flex fields [sys]",
                    ),
                ),
                (
                    "first_registration_date",
                    models.DateTimeField(help_text="Household first registration date [sys]"),
                ),
                (
                    "last_registration_date",
                    models.DateTimeField(help_text="Household last registration date [sys]"),
                ),
                (
                    "withdrawn",
                    models.BooleanField(default=False, help_text="Household withdrawn [sys]"),
                ),
                (
                    "withdrawn_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="Household withdrawn date [sys]",
                        null=True,
                    ),
                ),
                (
                    "longitude",
                    models.FloatField(blank=True, help_text="Household longitude [sys]", null=True),
                ),
                (
                    "latitude",
                    models.FloatField(blank=True, help_text="Household latitude [sys]", null=True),
                ),
                (
                    "deviceid",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Household deviceid [sys]",
                        max_length=250,
                    ),
                ),
                (
                    "name_enumerator",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Household name enumerator [sys]",
                        max_length=250,
                    ),
                ),
                (
                    "org_enumerator",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_org_enumerator_choices,
                        default="",
                        help_text="Household org enumerator [sys]",
                        max_length=250,
                    ),
                ),
                (
                    "org_name_enumerator",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Household org name enumerator [sys]",
                        max_length=250,
                    ),
                ),
                (
                    "kobo_submission_uuid",
                    models.UUIDField(
                        blank=True,
                        default=None,
                        help_text="Household Kobo submission uuid [sys]",
                        null=True,
                    ),
                ),
                (
                    "kobo_submission_time",
                    models.DateTimeField(
                        blank=True,
                        help_text="Household Kobo submission time [sys]",
                        max_length=150,
                        null=True,
                    ),
                ),
                (
                    "enumerator_rec_id",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Household enumerator record [sys]",
                        null=True,
                    ),
                ),
                (
                    "flex_registrations_record_id",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Household flex registrations record [sys]",
                        null=True,
                    ),
                ),
                (
                    "identification_key",
                    models.CharField(
                        blank=True,
                        help_text="Key used to identify Collisions in the system",
                        max_length=255,
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Household",
                "ordering": ("id",),
                "permissions": (
                    ("withdrawn", "Can withdrawn Household"),
                    ("sanity_check", "Sanity check Household"),
                    ("gdpr_remove", "GDPR remove Household data"),
                    ("logical_delete", "Logical delete Household"),
                    ("see_linked_objects", "Can see Linked Objects"),
                    ("reset_sync_date", "Can reset sync date"),
                ),
            },
            bases=(
                models.Model,
                hope.models.utils.AdminUrlMixin,
                hope.apps.household.mixins.HouseholdDeliveryDataMixin,
            ),
        ),
        migrations.CreateModel(
            name="HouseholdCollection",
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
                ("unicef_id", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="Individual",
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
                ("is_removed", models.BooleanField(default=False)),
                ("removed_date", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("last_sync_at", models.DateTimeField(blank=True, null=True)),
                (
                    "version",
                    concurrency.fields.IntegerVersionField(default=0, help_text="record revision number"),
                ),
                ("unicef_id", models.CharField(blank=True, max_length=255, null=True)),
                ("internal_data", models.JSONField(blank=True, default=dict)),
                (
                    "individual_id",
                    models.CharField(blank=True, help_text="Individual ID", max_length=255),
                ),
                (
                    "photo",
                    models.ImageField(
                        blank=True,
                        help_text="Photo",
                        max_length=255,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                (
                    "full_name",
                    models.CharField(
                        db_collation="und-ci-det",
                        help_text="Full Name of the Beneficiary",
                        max_length=255,
                        validators=[django.core.validators.MinLengthValidator(2)],
                    ),
                ),
                (
                    "given_name",
                    models.CharField(
                        blank=True,
                        db_collation="und-ci-det",
                        help_text="First name of the Beneficiary",
                        max_length=85,
                    ),
                ),
                (
                    "middle_name",
                    models.CharField(
                        blank=True,
                        db_collation="und-ci-det",
                        help_text="Middle name of the Beneficiary",
                        max_length=85,
                    ),
                ),
                (
                    "family_name",
                    models.CharField(
                        blank=True,
                        db_collation="und-ci-det",
                        help_text="Last name of the Beneficiary",
                        max_length=85,
                    ),
                ),
                (
                    "full_name_latin",
                    models.CharField(
                        blank=True,
                        db_collation="und-ci-det",
                        help_text="Full name of the Beneficiary Latin",
                        max_length=500,
                        null=True,
                        validators=[
                            django.core.validators.MinLengthValidator(2),
                            django.core.validators.RegexValidator(
                                code="invalid_name",
                                message="Only ASCII letters, spaces, hyphens, and apostrophes are allowed.",
                                regex="^[A-Za-z]+(?:[ '-][A-Za-z]+)*$",
                            ),
                        ],
                    ),
                ),
                (
                    "given_name_latin",
                    models.CharField(
                        blank=True,
                        db_collation="und-ci-det",
                        help_text="First name of the Beneficiary Latin",
                        max_length=150,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid_name",
                                message="Only ASCII letters, spaces, hyphens, and apostrophes are allowed.",
                                regex="^[A-Za-z]+(?:[ '-][A-Za-z]+)*$",
                            )
                        ],
                    ),
                ),
                (
                    "middle_name_latin",
                    models.CharField(
                        blank=True,
                        db_collation="und-ci-det",
                        help_text="Middle name of the Beneficiary Latin",
                        max_length=150,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid_name",
                                message="Only ASCII letters, spaces, hyphens, and apostrophes are allowed.",
                                regex="^[A-Za-z]+(?:[ '-][A-Za-z]+)*$",
                            )
                        ],
                    ),
                ),
                (
                    "family_name_latin",
                    models.CharField(
                        blank=True,
                        db_collation="und-ci-det",
                        help_text="Last name of the Beneficiary Latin",
                        max_length=150,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid_name",
                                message="Only ASCII letters, spaces, hyphens, and apostrophes are allowed.",
                                regex="^[A-Za-z]+(?:[ '-][A-Za-z]+)*$",
                            )
                        ],
                    ),
                ),
                (
                    "sex",
                    models.CharField(
                        choices=hope.apps.household.const.get_sex_choices,
                        help_text="Beneficiary gender",
                        max_length=255,
                    ),
                ),
                ("birth_date", models.DateField(help_text="Beneficiary date of birth")),
                (
                    "estimated_birth_date",
                    models.BooleanField(default=False, help_text="Estimated birth date flag"),
                ),
                (
                    "marital_status",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_marital_status_choices,
                        default="",
                        help_text="Beneficiary marital status",
                        max_length=255,
                    ),
                ),
                (
                    "phone_no",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True,
                        help_text="Beneficiary phone number",
                        max_length=128,
                        region=None,
                    ),
                ),
                (
                    "phone_no_alternative",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True,
                        help_text="Beneficiary phone number alternative",
                        max_length=128,
                        region=None,
                    ),
                ),
                (
                    "email",
                    models.CharField(
                        blank=True,
                        help_text="Beneficiary email address",
                        max_length=255,
                    ),
                ),
                (
                    "payment_delivery_phone_no",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True,
                        help_text="Beneficiary contact phone number",
                        max_length=128,
                        null=True,
                        region=None,
                    ),
                ),
                (
                    "relationship",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_relationship_choices,
                        help_text="This represents the MEMBER relationship. can be blank\n            as well if household is null!",
                        max_length=255,
                    ),
                ),
                (
                    "work_status",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_work_status_choices,
                        default="NOT_PROVIDED",
                        help_text="Work status",
                        max_length=20,
                    ),
                ),
                (
                    "pregnant",
                    models.BooleanField(blank=True, help_text="Pregnant status", null=True),
                ),
                (
                    "fchild_hoh",
                    models.BooleanField(
                        default=False,
                        help_text="Child is female and Head of Household flag",
                    ),
                ),
                (
                    "child_hoh",
                    models.BooleanField(default=False, help_text="Child is Head of Household flag"),
                ),
                (
                    "disability",
                    models.CharField(
                        choices=hope.apps.household.const.get_disability_choices,
                        default="not disabled",
                        help_text="Disability status",
                        max_length=20,
                    ),
                ),
                (
                    "observed_disability",
                    multiselectfield.db.fields.MultiSelectField(
                        choices=hope.apps.household.const.get_observed_disability_choices,
                        default="NONE",
                        help_text="Observed disability status",
                        max_length=58,
                    ),
                ),
                (
                    "disability_certificate_picture",
                    models.ImageField(
                        blank=True,
                        help_text="Disability certificate picture",
                        max_length=255,
                        null=True,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                (
                    "seeing_disability",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_severity_of_disability_choices,
                        help_text="Seeing disability",
                        max_length=50,
                    ),
                ),
                (
                    "hearing_disability",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_severity_of_disability_choices,
                        help_text="Hearing disability",
                        max_length=50,
                    ),
                ),
                (
                    "physical_disability",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_severity_of_disability_choices,
                        help_text="Physical disability",
                        max_length=50,
                    ),
                ),
                (
                    "memory_disability",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_severity_of_disability_choices,
                        help_text="Memory disability",
                        max_length=50,
                    ),
                ),
                (
                    "selfcare_disability",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_severity_of_disability_choices,
                        help_text="Selfcare disability",
                        max_length=50,
                    ),
                ),
                (
                    "comms_disability",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_severity_of_disability_choices,
                        help_text="Comms disability",
                        max_length=50,
                    ),
                ),
                (
                    "who_answers_phone",
                    models.CharField(blank=True, help_text="Who answers phone number", max_length=150),
                ),
                (
                    "who_answers_alt_phone",
                    models.CharField(
                        blank=True,
                        help_text="Who answers alternative phone number",
                        max_length=150,
                    ),
                ),
                (
                    "preferred_language",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.core.languages.Languages.get_tuple,
                        help_text="Preferred language",
                        max_length=6,
                        null=True,
                    ),
                ),
                (
                    "relationship_confirmed",
                    models.BooleanField(default=False, help_text="Relationship confirmed status"),
                ),
                (
                    "duplicate",
                    models.BooleanField(default=False, help_text="Duplicate status [sys]"),
                ),
                (
                    "duplicate_date",
                    models.DateTimeField(blank=True, help_text="Duplicate date [sys]", null=True),
                ),
                (
                    "withdrawn",
                    models.BooleanField(default=False, help_text="Withdrawn status [sys]"),
                ),
                (
                    "withdrawn_date",
                    models.DateTimeField(blank=True, help_text="Withdrawn date [sys]", null=True),
                ),
                (
                    "flex_fields",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=hope.apps.core.utils.FlexFieldsEncoder,
                        help_text="FlexFields JSON representation [sys]",
                    ),
                ),
                (
                    "phone_no_valid",
                    models.BooleanField(
                        blank=True,
                        help_text="Beneficiary phone number valid [sys]",
                        null=True,
                    ),
                ),
                (
                    "phone_no_alternative_valid",
                    models.BooleanField(
                        blank=True,
                        help_text="Beneficiary phone number alternative valid [sys]",
                        null=True,
                    ),
                ),
                (
                    "first_registration_date",
                    models.DateField(help_text="First registration date [sys]"),
                ),
                (
                    "last_registration_date",
                    models.DateField(help_text="Last registration date [sys]"),
                ),
                (
                    "enrolled_in_nutrition_programme",
                    models.BooleanField(
                        blank=True,
                        help_text="Enrolled in nutrition program [sys]",
                        null=True,
                    ),
                ),
                (
                    "deduplication_golden_record_status",
                    models.CharField(
                        choices=hope.apps.household.const.get_deduplication_golden_record_status_choices,
                        default="UNIQUE",
                        help_text="Deduplication golden record status [sys]",
                        max_length=50,
                    ),
                ),
                (
                    "deduplication_batch_status",
                    models.CharField(
                        choices=hope.apps.household.const.get_deduplication_batch_status_choices,
                        default="UNIQUE_IN_BATCH",
                        help_text="Deduplication batch status [sys]",
                        max_length=50,
                    ),
                ),
                (
                    "deduplication_golden_record_results",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Deduplication golden record results [sys]",
                    ),
                ),
                (
                    "deduplication_batch_results",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Deduplication batch results [sys]",
                    ),
                ),
                (
                    "biometric_deduplication_golden_record_status",
                    models.CharField(
                        choices=hope.apps.household.const.get_deduplication_golden_record_status_choices,
                        default="NOT_PROCESSED",
                        help_text="Deduplication golden record status [sys]",
                        max_length=50,
                    ),
                ),
                (
                    "biometric_deduplication_batch_status",
                    models.CharField(
                        choices=hope.apps.household.const.get_deduplication_batch_status_choices,
                        default="NOT_PROCESSED",
                        help_text="Deduplication batch status [sys]",
                        max_length=50,
                    ),
                ),
                (
                    "biometric_deduplication_golden_record_results",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Deduplication golden record results [sys]",
                    ),
                ),
                (
                    "biometric_deduplication_batch_results",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Deduplication batch results [sys]",
                    ),
                ),
                (
                    "imported_individual_id",
                    models.UUIDField(blank=True, help_text="Imported individual ID [sys]", null=True),
                ),
                (
                    "sanction_list_possible_match",
                    models.BooleanField(default=False, help_text="Sanction list possible match [sys]"),
                ),
                (
                    "sanction_list_confirmed_match",
                    models.BooleanField(default=False, help_text="Sanction list confirmed match [sys]"),
                ),
                (
                    "detail_id",
                    models.CharField(
                        blank=True,
                        help_text="Kobo asset ID, Xlsx row ID, Aurora registration ID [sys]",
                        max_length=150,
                        null=True,
                    ),
                ),
                (
                    "originating_id",
                    models.CharField(
                        blank=True,
                        help_text="A unified external reference with a fixed-length source prefix (XLS, KOB, or AUR)\n                     and a source-specific identifier separated by '#', e.g., 'KOB#321#123'.",
                        max_length=150,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="originating_id must start with: KOB, AUR, XLS, API",
                                regex="^(KOB|AUR|XLS|API)#.+$",
                            )
                        ],
                    ),
                ),
                (
                    "country_workspace_id",
                    models.CharField(
                        blank=True,
                        help_text="Primary key of the Individual on the originating Country Workspace system. Used as the reference key when communicating with the Deduplication Engine.",
                        max_length=150,
                        null=True,
                    ),
                ),
                (
                    "program_registration_id",
                    models.CharField(
                        blank=True,
                        db_collation="und-ci-det",
                        help_text="Beneficiary Program Registration ID [sys]",
                        max_length=100,
                        null=True,
                        verbose_name="Beneficiary Program Registration Id",
                    ),
                ),
                (
                    "age_at_registration",
                    models.PositiveSmallIntegerField(blank=True, help_text="Age at registration [sys]", null=True),
                ),
                (
                    "origin_unicef_id",
                    models.CharField(
                        blank=True,
                        help_text="Original unicef_id [sys]",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "is_migration_handled",
                    models.BooleanField(default=False, help_text="Migration status [sys]"),
                ),
                (
                    "migrated_at",
                    models.DateTimeField(blank=True, help_text="Migrated at [sys]", null=True),
                ),
                (
                    "identification_key",
                    models.CharField(
                        blank=True,
                        help_text="Key used to identify Collisions in the system",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "vector_column",
                    django.contrib.postgres.search.SearchVectorField(
                        help_text="Database vector column for search [sys]", null=True
                    ),
                ),
            ],
            options={
                "verbose_name": "Individual",
                "ordering": ("id",),
                "permissions": (
                    ("update_individual_iban", "Can update individual IBAN"),
                    ("individual_sanity_check", "Can check individual sanity"),
                    ("see_linked_objects", "Can see linked objects"),
                    ("reset_sync_date", "Can reset sync date"),
                ),
            },
            bases=(
                models.Model,
                hope.models.utils.AdminUrlMixin,
                hope.apps.household.mixins.IndividualDeliveryDataMixin,
            ),
        ),
        migrations.CreateModel(
            name="IndividualCollection",
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
                ("unicef_id", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="IndividualIdentity",
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
                (
                    "rdi_merge_status",
                    models.CharField(
                        blank=True,
                        choices=hope.models.utils.get_merge_status_choices,
                        default="PENDING",
                        max_length=10,
                    ),
                ),
                ("is_removed", models.BooleanField(default=False)),
                ("removed_date", models.DateTimeField(blank=True, null=True)),
                ("number", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "Individual Identities",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="IndividualRoleInHousehold",
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
                ("is_removed", models.BooleanField(default=False)),
                ("removed_date", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("last_sync_at", models.DateTimeField(blank=True, null=True)),
                (
                    "role",
                    models.CharField(
                        blank=True,
                        choices=hope.apps.household.const.get_role_choices,
                        max_length=255,
                    ),
                ),
            ],
            options={
                "ordering": ("-role", "id"),
                "permissions": (("reset_sync_date", "Can reset sync date"),),
            },
        ),
        migrations.CreateModel(
            name="XlsxUpdateFile",
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
                    "file",
                    models.FileField(
                        max_length=255,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                (
                    "xlsx_match_columns",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=32),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="Document",
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
                ("is_removed", models.BooleanField(default=False)),
                ("removed_date", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("last_sync_at", models.DateTimeField(blank=True, null=True)),
                ("document_number", models.CharField(blank=True, max_length=255)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=hope.models.document.get_document_status_choices,
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "photo",
                    models.ImageField(
                        blank=True,
                        max_length=255,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                (
                    "cleared",
                    models.BooleanField(
                        default=False,
                        help_text="Cleared used to confirm FOSTER_CHILD relationship",
                    ),
                ),
                (
                    "cleared_date",
                    models.DateTimeField(blank=True, default=django.utils.timezone.now),
                ),
                ("issuance_date", models.DateTimeField(blank=True, null=True)),
                ("expiry_date", models.DateTimeField(blank=True, null=True)),
                (
                    "cleared_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "copied_from",
                    models.ForeignKey(
                        blank=True,
                        help_text="If this object was copied from another, this field will contain the object it was copied from.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="copied_to",
                        to="household.document",
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
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
    ]
