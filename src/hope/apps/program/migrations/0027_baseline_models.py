from decimal import Decimal
import uuid

import concurrency.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import strategy_field.fields

import hope.models.program
import hope.models.program_cycle
import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("program", "0002_migration"),
        ("program", "0003_migration"),
        ("program", "0004_migration"),
        ("program", "0005_migration"),
        ("program", "0006_migration"),
        ("program", "0007_migration"),
        ("program", "0008_migration"),
        ("program", "0009_migration"),
        ("program", "0010_migration"),
        ("program", "0011_migration"),
        ("program", "0012_migration"),
        ("program", "0013_migration"),
        ("program", "0014_migration"),
        ("program", "0015_migration"),
        ("program", "0016_migration"),
        ("program", "0017_migration"),
        ("program", "0018_migration"),
        ("program", "0019_migration"),
        ("program", "0020_migration"),
        ("program", "0021_disable_biometric_dedup_for_non_cw"),
        ("program", "0022_migration"),
        ("program", "0023_migration"),
        ("program", "0024_migration"),
        ("program", "0025_migration"),
        ("program", "0026_migration"),
    ]

    dependencies = [
        ("core", "0044_baseline_models"),
        ("geo", "0010_baseline_models"),
        ("payment", "0084_baseline_models"),
        ("sanction_list", "0010_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE COLLATION IF NOT EXISTS \"und-ci-det\" (provider = icu, locale = 'und-u-ks-level2', deterministic = true);",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name="BeneficiaryGroup",
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
                ("group_label", models.CharField(max_length=255)),
                ("group_label_plural", models.CharField(max_length=255)),
                ("member_label", models.CharField(max_length=255)),
                ("member_label_plural", models.CharField(max_length=255)),
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text="Inactive Payee Labels cannot be used in new programs",
                    ),
                ),
                (
                    "data_collecting_types",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Leave empty to allow every Data Collecting Type of the Payee Type",
                        related_name="payee_labels",
                        to="core.datacollectingtype",
                    ),
                ),
                (
                    "payee_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payee_labels",
                        to="core.payeetype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Payee Label",
                "verbose_name_plural": "Payee Labels",
                "ordering": ("name",),
                "permissions": (("reset_sync_date", "Can reset sync date"),),
            },
        ),
        migrations.CreateModel(
            name="Program",
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
                ("last_sync_at", models.DateTimeField(blank=True, null=True)),
                (
                    "version",
                    concurrency.fields.IntegerVersionField(default=0, help_text="record revision number"),
                ),
                (
                    "name",
                    models.CharField(
                        db_collation="und-ci-det",
                        help_text="Program name",
                        max_length=255,
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
                ("code", models.CharField(help_text="Program code", max_length=4)),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.program.get_status_choices,
                        help_text="Program status",
                        max_length=10,
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        help_text="Program description",
                        max_length=255,
                        validators=[
                            django.core.validators.MinLengthValidator(3),
                            django.core.validators.MaxLengthValidator(255),
                        ],
                    ),
                ),
                ("start_date", models.DateField(help_text="Program start date")),
                (
                    "end_date",
                    models.DateField(blank=True, help_text="Program end date", null=True),
                ),
                (
                    "sector",
                    models.CharField(
                        choices=hope.models.program.get_sector_choices,
                        help_text="Program sector",
                        max_length=50,
                    ),
                ),
                (
                    "budget",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Program budget",
                        max_digits=11,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                (
                    "frequency_of_payments",
                    models.CharField(
                        choices=hope.models.program.get_frequency_of_payments_choices,
                        help_text="Program frequency of payments",
                        max_length=50,
                    ),
                ),
                (
                    "scope",
                    models.CharField(
                        blank=True,
                        choices=hope.models.program.get_scope_choices,
                        help_text="Program scope",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "partner_access",
                    models.CharField(
                        choices=hope.models.program.get_partner_access_choices,
                        default="SELECTED_PARTNERS_ACCESS",
                        help_text="Program partner access",
                        max_length=50,
                    ),
                ),
                ("cash_plus", models.BooleanField(help_text="Program cash+")),
                (
                    "population_goal",
                    models.PositiveIntegerField(help_text="Program population goal"),
                ),
                (
                    "administrative_areas_of_implementation",
                    models.CharField(
                        blank=True,
                        help_text="Program administrative area of implementation",
                        max_length=255,
                        validators=[
                            django.core.validators.MinLengthValidator(3),
                            django.core.validators.MaxLengthValidator(255),
                        ],
                    ),
                ),
                (
                    "biometric_deduplication_enabled",
                    models.BooleanField(default=False, help_text="Enable Deduplication of Face Images"),
                ),
                (
                    "collision_detector",
                    strategy_field.fields.StrategyField(
                        default="hope.apps.program.collision_detectors.NoopCollisionDetector",
                        help_text="Object which detects collisions",
                    ),
                ),
                (
                    "identification_key_individual_label",
                    models.CharField(
                        blank=True,
                        help_text="Label for identification key used for individuals",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "is_visible",
                    models.BooleanField(default=True, help_text="Program is visible in UI [sys]"),
                ),
                (
                    "household_count",
                    models.PositiveIntegerField(default=0, help_text="Program household count [sys]"),
                ),
                (
                    "individual_count",
                    models.PositiveIntegerField(default=0, help_text="Program individual count [sys]"),
                ),
                (
                    "reconciliation_window_in_days",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Payment Plan reconciliation window in days",
                    ),
                ),
                (
                    "send_reconciliation_window_expiry_notifications",
                    models.BooleanField(
                        default=False,
                        help_text="Send Payment Plan reconciliation window expiry notifications",
                    ),
                ),
                (
                    "admin_areas",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Admin areas",
                        related_name="programs",
                        to="geo.area",
                    ),
                ),
                (
                    "beneficiary_group",
                    models.ForeignKey(
                        help_text="Program payee label",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="programs",
                        to="program.beneficiarygroup",
                    ),
                ),
                (
                    "business_area",
                    models.ForeignKey(
                        help_text="Business area",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.businessarea",
                    ),
                ),
                (
                    "data_collecting_type",
                    models.ForeignKey(
                        help_text="Program data collecting type",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="programs",
                        to="core.datacollectingtype",
                    ),
                ),
                (
                    "payment_plan_purposes",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Payment plan purposes available within program",
                        related_name="programs",
                        to="payment.paymentplanpurpose",
                    ),
                ),
                (
                    "sanction_lists",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Program sanction lists",
                        related_name="programs",
                        to="sanction_list.sanctionlist",
                    ),
                ),
            ],
            options={
                "verbose_name": "Programme",
                "ordering": ("id",),
                "permissions": [
                    ("enroll_beneficiaries", "Can enroll beneficiaries"),
                    (
                        "can_bulk_upload_individual_photos",
                        "Can bulk upload Individual photos",
                    ),
                    ("reset_sync_date", "Can reset sync date"),
                ],
            },
            bases=(models.Model, hope.models.utils.AdminUrlMixin),
        ),
        migrations.CreateModel(
            name="ProgramCycle",
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
                    "title",
                    models.CharField(
                        blank=True,
                        default="Default Programme Cycle",
                        max_length=255,
                        null=True,
                        verbose_name="Title",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.program_cycle.get_program_cycle_status_choices,
                        default="DRAFT",
                        max_length=10,
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cycles",
                        to="program.program",
                    ),
                ),
            ],
            options={
                "verbose_name": "Programme Cycle",
                "ordering": ["start_date"],
                "permissions": (("reset_sync_date", "Can reset sync date"),),
            },
            bases=(hope.models.utils.AdminUrlMixin, models.Model),
        ),
        migrations.AddIndex(
            model_name="beneficiarygroup",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="program_beneficiarygroup_created_at_b78ee65a",
            ),
        ),
        migrations.AddIndex(
            model_name="beneficiarygroup",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="program_beneficiarygroup_updated_at_c80e3d34",
            ),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="program_program_created_at_0fb0bad5"),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="program_program_updated_at_244df9de"),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(fields=["name"], name="program_program_name_2670ab01"),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(fields=["code"], name="program_program_code_b7abf396"),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(
                fields=["code"],
                name="program_program_code_b7abf396_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(fields=["status"], name="program_program_status_d116e0a6"),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="program_program_status_d116e0a6_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(fields=["start_date"], name="program_program_start_date_f53642aa"),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(fields=["end_date"], name="program_program_end_date_449c52ec"),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(fields=["sector"], name="program_program_sector_2fb1058e"),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(
                fields=["sector"],
                name="program_program_sector_2fb1058e_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="program",
            index=hope.models.utils.LongNameIndex(fields=["budget"], name="program_program_budget_3757bcc6"),
        ),
        migrations.AddConstraint(
            model_name="program",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_removed", False)),
                fields=("name", "business_area", "is_removed"),
                name="unique_for_program_if_not_removed",
            ),
        ),
        migrations.AddConstraint(
            model_name="program",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_removed", False)),
                fields=("business_area", "code"),
                name="unique_for_business_area_and_code_if_not_removed",
            ),
        ),
        migrations.AddIndex(
            model_name="programcycle",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="program_programcycle_created_at_f18c5d99"
            ),
        ),
        migrations.AddIndex(
            model_name="programcycle",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="program_programcycle_updated_at_89ffd4dc"
            ),
        ),
        migrations.AddIndex(
            model_name="programcycle",
            index=hope.models.utils.LongNameIndex(fields=["unicef_id"], name="program_programcycle_unicef_id_65638c2c"),
        ),
        migrations.AddIndex(
            model_name="programcycle",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="program_programcycle_unicef_id_65638c2c_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="programcycle",
            index=hope.models.utils.LongNameIndex(fields=["status"], name="program_programcycle_status_c6ee3e75"),
        ),
        migrations.AddIndex(
            model_name="programcycle",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="program_programcycle_status_c6ee3e75_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddConstraint(
            model_name="programcycle",
            constraint=models.UniqueConstraint(
                fields=("title", "program"),
                name="program_cycle_title_unique_per_program",
            ),
        ),
        # unicef_id of programme cycles, numbered per business area from a sequence created by a core trigger.
        migrations.RunSQL(
            sql=[
                """CREATE OR REPLACE FUNCTION program_cycle_fill_unicef_id_per_business_area_seq()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
                DECLARE
                    businessAreaID varchar;
                    businessAreaCode varchar;
                BEGIN
                    SELECT INTO businessAreaID p.business_area_id FROM program_program p WHERE p.id = NEW.program_id;
                    SELECT INTO businessAreaCode ba.code FROM core_businessarea ba WHERE ba.id = businessAreaID::uuid;
                    NEW.unicef_id := format('PC-%s-%s-%s', trim(businessAreaCode), to_char(NEW.created_at, 'yy'), trim(replace(to_char(nextval('program_cycle_business_area_seq_' || translate(businessAreaID::text, '-','_')),'000000'),',','.')));
                    RETURN NEW;
                END;
                $function$""",
                "CREATE TRIGGER program_cycle_fill_unicef_id_per_business_area_seq BEFORE INSERT ON program_programcycle FOR EACH ROW EXECUTE FUNCTION program_cycle_fill_unicef_id_per_business_area_seq()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
