import uuid

import concurrency.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields

from hope.apps.core.migration_operations import RunSQLAfterDeferred
import hope.apps.core.upload_paths
import hope.models.deduplication_engine_similarity_pair
import hope.models.import_data
import hope.models.registration_data_import
import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("registration_data", "0001_migration"),
        ("registration_data", "0002_migration"),
        ("registration_data", "0003_migration"),
        ("registration_data", "0004_migration"),
        ("registration_data", "0005_migration"),
        ("registration_data", "0006_migration"),
        ("registration_data", "0007_migration"),
        ("registration_data", "0008_migration"),
        ("registration_data", "0009_migration"),
        ("registration_data", "0010_migration"),
        ("registration_data", "0011_migration"),
        ("registration_data", "0012_migration"),
        ("registration_data", "0013_migration"),
        ("registration_data", "0014_migration"),
        ("registration_data", "0015_migration"),
        ("registration_data", "0016_migration"),
        ("registration_data", "0017_migration"),
        ("registration_data", "0018_migration"),
        ("registration_data", "0019_migration"),
        ("registration_data", "0020_migration"),
        ("registration_data", "0021_migration"),
    ]

    dependencies = [
        ("core", "0044_baseline_models"),
        ("household", "0056_baseline_models"),
        ("program", "0027_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Collation of the db_collation fields below.
        migrations.RunSQL(
            sql="CREATE COLLATION IF NOT EXISTS \"und-ci-det\" (provider = icu, locale = 'und-u-ks-level2', deterministic = true);",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name="ImportData",
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
                        choices=hope.models.import_data.get_status_choices,
                        default="FINISHED",
                        max_length=40,
                    ),
                ),
                ("business_area_slug", models.CharField(blank=True, max_length=200)),
                (
                    "data_type",
                    models.CharField(
                        choices=hope.models.import_data.get_data_type_choices,
                        default="XLSX",
                        max_length=4,
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        max_length=255,
                        null=True,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                (
                    "number_of_households",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "number_of_individuals",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("error", models.TextField(blank=True)),
                ("validation_errors", models.TextField(blank=True)),
                ("delivery_mechanisms_validation_errors", models.TextField(blank=True)),
                ("created_by_id", models.UUIDField(blank=True, null=True)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="KoboImportedSubmission",
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
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("kobo_submission_uuid", models.UUIDField()),
                ("kobo_asset_id", models.CharField(max_length=150)),
                ("kobo_submission_time", models.DateTimeField()),
                ("amended", models.BooleanField(blank=True, default=False)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="RegistrationDataImport",
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
                    "name",
                    models.CharField(
                        db_collation="und-ci-det",
                        max_length=255,
                        unique=True,
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
                    "status",
                    models.CharField(
                        choices=hope.models.registration_data_import.get_status_choices,
                        default="IN_REVIEW",
                        max_length=255,
                    ),
                ),
                ("import_date", models.DateTimeField(auto_now_add=True)),
                (
                    "data_source",
                    models.CharField(
                        choices=hope.models.registration_data_import.get_data_source_choices,
                        max_length=255,
                    ),
                ),
                ("import_from_ids", models.TextField(blank=True, null=True)),
                (
                    "exclude_external_collectors",
                    models.BooleanField(
                        default=False,
                        help_text="Exclude external alternate collectors from the RDI. This is used for the RDI created from the program population.",
                    ),
                ),
                ("pull_pictures", models.BooleanField(default=True)),
                ("screen_beneficiary", models.BooleanField(default=False)),
                (
                    "excluded",
                    models.BooleanField(default=False, help_text="Exclude RDI in UI"),
                ),
                ("erased", models.BooleanField(default=False, help_text="Abort RDI")),
                (
                    "refuse_reason",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("error_message", models.TextField(blank=True)),
                (
                    "sentry_id",
                    models.CharField(blank=True, default="", max_length=100, null=True),
                ),
                ("number_of_individuals", models.PositiveIntegerField()),
                ("number_of_households", models.PositiveIntegerField()),
                ("batch_duplicates", models.PositiveIntegerField(default=0)),
                ("batch_possible_duplicates", models.PositiveIntegerField(default=0)),
                ("batch_unique", models.PositiveIntegerField(default=0)),
                ("golden_record_duplicates", models.PositiveIntegerField(default=0)),
                (
                    "golden_record_possible_duplicates",
                    models.PositiveIntegerField(default=0),
                ),
                ("golden_record_unique", models.PositiveIntegerField(default=0)),
                (
                    "dedup_engine_batch_duplicates",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "dedup_engine_golden_record_duplicates",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "country_workspace_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
            options={
                "verbose_name": "Registration data import",
                "ordering": ("id",),
                "permissions": (
                    ("rerun_rdi", "Can Rerun RDI"),
                    ("delete_rdi", "Can Delete RDI"),
                    ("delete_merged_rdi", "Can Delete Merged RDI"),
                ),
            },
            bases=(models.Model, hope.models.utils.AdminUrlMixin),
        ),
        migrations.CreateModel(
            name="BiometricDedupeSimilarityPair",
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
                    "similarity_score",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
                (
                    "status_code",
                    models.CharField(
                        choices=hope.models.deduplication_engine_similarity_pair.BiometricDedupeSimilarityPair.StatusCode._status_code_choices,
                        max_length=20,
                    ),
                ),
                (
                    "individual1",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="biometric_duplicates_1",
                        to="household.individual",
                    ),
                ),
                (
                    "individual2",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="biometric_duplicates_2",
                        to="household.individual",
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deduplication_engine_similarity_pairs",
                        to="program.program",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="KoboImportData",
            fields=[
                (
                    "importdata_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="registration_data.importdata",
                    ),
                ),
                ("kobo_asset_id", models.CharField(max_length=100)),
                ("only_active_submissions", models.BooleanField(default=True)),
                ("pull_pictures", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("id",),
            },
            bases=("registration_data.importdata",),
        ),
        migrations.AddIndex(
            model_name="importdata",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="registration_data_importdata_created_at_22e35892",
            ),
        ),
        migrations.AddIndex(
            model_name="importdata",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="registration_data_importdata_updated_at_631db42b",
            ),
        ),
        migrations.AddField(
            model_name="koboimportedsubmission",
            name="imported_household",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="household.household",
            ),
        ),
        migrations.AddField(
            model_name="registrationdataimport",
            name="business_area",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="core.businessarea"),
        ),
        migrations.AddField(
            model_name="registrationdataimport",
            name="import_data",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registration_data_import_hope",
                to="registration_data.importdata",
            ),
        ),
        migrations.AddField(
            model_name="registrationdataimport",
            name="imported_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registration_data_imports",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="registrationdataimport",
            name="program",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="registration_imports",
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="koboimportedsubmission",
            name="registration_data_import",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="registration_data.registrationdataimport",
            ),
        ),
        migrations.AddConstraint(
            model_name="biometricdedupesimilaritypair",
            constraint=models.CheckConstraint(
                condition=models.Q(("individual1__lt", models.F("individual2"))),
                name="individual1_lt_individual2",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="biometricdedupesimilaritypair",
            unique_together={("individual1", "individual2")},
        ),
        migrations.AddIndex(
            model_name="registrationdataimport",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="registration_data_registrationdataimport_created_at_d8c2eb4f",
            ),
        ),
        migrations.AddIndex(
            model_name="registrationdataimport",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="registration_data_registrationdataimport_updated_at_442895a8",
            ),
        ),
        migrations.AddIndex(
            model_name="registrationdataimport",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="registration_data_registrationdataimport_status_e9087d0c",
            ),
        ),
        migrations.AddIndex(
            model_name="registrationdataimport",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="registration_data_registrationdataimport_status_e9087d0c_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="registrationdataimport",
            index=hope.models.utils.LongNameIndex(
                fields=["import_date"],
                name="registration_data_registrationdataimport_import_date_1ef9a06e",
            ),
        ),
        migrations.AddIndex(
            model_name="registrationdataimport",
            index=hope.models.utils.LongNameIndex(
                fields=["number_of_individuals"],
                name="registration_data_registra_number_of_individuals_51a4efa0",
            ),
        ),
        migrations.AddIndex(
            model_name="registrationdataimport",
            index=hope.models.utils.LongNameIndex(
                fields=["number_of_households"],
                name="registration_data_registra_number_of_households_4ad75097",
            ),
        ),
        migrations.AddConstraint(
            model_name="registrationdataimport",
            constraint=models.UniqueConstraint(
                condition=models.Q(("country_workspace_id__isnull", False)),
                fields=("country_workspace_id",),
                name="unique_rdi_country_workspace_id",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="registrationdataimport",
            unique_together={("name", "business_area")},
        ),
        migrations.AddIndex(
            model_name="koboimportedsubmission",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="registration_data_koboimportedsubmission_created_at_b80e8453",
            ),
        ),
        # Names that RenameModel and RenameField left behind in the replaced history. Every existing database
        # has them, so a new one gets them too. Renaming the index of a primary key or unique constraint
        # renames the constraint with it.
        RunSQLAfterDeferred(
            sql=[
                "ALTER INDEX IF EXISTS registration_data_biometri_individual1_id_4eff8bdd RENAME TO registration_data_deduplic_individual1_id_b2974985",
                "ALTER INDEX IF EXISTS registration_data_biometri_individual2_id_bde35c9d RENAME TO registration_data_deduplic_individual2_id_f8a2cfbf",
                "ALTER INDEX IF EXISTS registration_data_biometri_program_id_984ceadf RENAME TO registration_data_deduplic_program_id_62661470",
                "ALTER INDEX IF EXISTS registration_data_biometricdedupesimilaritypair_pkey RENAME TO registration_data_deduplicationenginesimilaritypair_pkey",
                "ALTER INDEX IF EXISTS registration_data_biomet_individual1_id_individua_b628a04d_uniq RENAME TO registration_data_dedupl_individual1_id_individua_ec363966_uniq",
                "ALTER SEQUENCE IF EXISTS registration_data_biometricdedupesimilaritypair_id_seq RENAME TO registration_data_deduplicationenginesimilaritypair_id_seq",
                """DO $$
DECLARE
    renames text[][] := ARRAY[
        ['registration_data_biometricdedupesimilaritypair', 'registration_data_bi_individual1_id_4eff8bdd_fk_household', 'registration_data_de_individual1_id_b2974985_fk_household'],
        ['registration_data_biometricdedupesimilaritypair', 'registration_data_bi_individual2_id_bde35c9d_fk_household', 'registration_data_de_individual2_id_f8a2cfbf_fk_household'],
        ['registration_data_biometricdedupesimilaritypair', 'registration_data_bi_program_id_984ceadf_fk_program_p', 'registration_data_de_program_id_62661470_fk_program_p']
    ];
    r text[];
BEGIN
    FOREACH r SLICE 1 IN ARRAY renames LOOP
        IF EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid = r[1]::regclass AND conname = r[2]) THEN
            EXECUTE format('ALTER TABLE %I RENAME CONSTRAINT %I TO %I', r[1], r[2], r[3]);
        END IF;
    END LOOP;
END $$""",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
