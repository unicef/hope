from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.functions.text
import mptt.fields

from hope.apps.core.currencies import CURRENCIES
from hope.apps.core.migration_operations import RunSQLAfterDeferred
import hope.models.utils


def seed_reference_data(apps, schema_editor):
    """Create the currencies, payee types and head of facility collecting type of a new database."""
    Currency = apps.get_model("core", "Currency")
    PayeeType = apps.get_model("core", "PayeeType")
    DataCollectingType = apps.get_model("core", "DataCollectingType")

    Currency.objects.bulk_create(
        [Currency(code=code, name=name, is_crypto=is_crypto, vision_code=code) for code, name, is_crypto in CURRENCIES],
        ignore_conflicts=True,
    )

    PayeeType.objects.get_or_create(name="Household", defaults={"gl_code": "7700410", "weight": 30})
    PayeeType.objects.get_or_create(name="Incentive Payee", defaults={"gl_code": "7700430", "weight": 20})
    organization, _ = PayeeType.objects.get_or_create(
        name="Organization", defaults={"gl_code": "7700430", "weight": 10}
    )
    head_of_facility, _ = DataCollectingType.objects.get_or_create(
        code="head_of_facility",
        defaults={
            "label": "Head of Facility",
            "description": "Head of Facility / Authorized Representative",
            "type": "STANDARD",
            "active": True,
            "payee_type": organization,
        },
    )
    # The post_save receiver that makes a collecting type compatible with itself does not run in migrations.
    head_of_facility.compatible_types.add(head_of_facility)
    PayeeType.objects.filter(pk=organization.pk, default_data_collecting_type__isnull=True).update(
        default_data_collecting_type=head_of_facility
    )


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("core", "0001_migration"),
    ]

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("core", "0044_baseline_models"),
        ("geo", "0010_baseline_models"),
        ("program", "0027_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="asyncjob",
            name="program",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="program.program",
            ),
        ),
        migrations.CreateModel(
            name="AsyncRetryJob",
            fields=[],
            options={
                "verbose_name": "Retry Asynchronous Job",
                "verbose_name_plural": "Retry Asynchronous Jobs",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.asyncjob",),
        ),
        migrations.AddField(
            model_name="businessarea",
            name="countries",
            field=models.ManyToManyField(related_name="business_areas", to="geo.country"),
        ),
        migrations.AddField(
            model_name="businessarea",
            name="office_country",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="business_area",
                to="geo.country",
            ),
        ),
        migrations.AddField(
            model_name="businessarea",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to="core.businessarea",
            ),
        ),
        migrations.AddField(
            model_name="businessarea",
            name="payment_countries",
            field=models.ManyToManyField(related_name="payment_business_areas", to="geo.country"),
        ),
        migrations.AddField(
            model_name="countrycodemap",
            name="country",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="geo.country",
            ),
        ),
        migrations.AddIndex(
            model_name="currency",
            index=hope.models.utils.LongNameIndex(fields=["code"], name="core_currency_code_0c3ee469"),
        ),
        migrations.AddIndex(
            model_name="currency",
            index=hope.models.utils.LongNameIndex(
                fields=["code"],
                name="core_currency_code_0c3ee469_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddConstraint(
            model_name="currency",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("code"),
                condition=models.Q(("active", True)),
                name="unique_code_active",
            ),
        ),
        migrations.AddConstraint(
            model_name="currency",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("vision_code"),
                name="unique_vision_code",
            ),
        ),
        migrations.AddField(
            model_name="datacollectingtype",
            name="compatible_types",
            field=models.ManyToManyField(blank=True, to="core.datacollectingtype"),
        ),
        migrations.AddField(
            model_name="datacollectingtype",
            name="limit_to",
            field=models.ManyToManyField(blank=True, related_name="data_collecting_types", to="core.businessarea"),
        ),
        migrations.AddField(
            model_name="filetemp",
            name="content_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AddField(
            model_name="filetemp",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="flexibleattribute",
            name="program",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pdu_fields",
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="flexibleattributechoice",
            name="flex_attributes",
            field=models.ManyToManyField(related_name="choices", to="core.flexibleattribute"),
        ),
        migrations.AddField(
            model_name="flexibleattributegroup",
            name="parent",
            field=mptt.fields.TreeForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="core.flexibleattributegroup",
                verbose_name="Parent",
            ),
        ),
        migrations.AddField(
            model_name="flexibleattribute",
            name="group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="flex_attributes",
                to="core.flexibleattributegroup",
            ),
        ),
        migrations.AddField(
            model_name="payeetype",
            name="default_data_collecting_type",
            field=models.ForeignKey(
                blank=True,
                help_text="Data Collecting Type preselected when this Payee Type is chosen",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.datacollectingtype",
            ),
        ),
        migrations.AddField(
            model_name="datacollectingtype",
            name="payee_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="data_collecting_types",
                to="core.payeetype",
            ),
        ),
        migrations.AddField(
            model_name="periodicasyncjob",
            name="content_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AddField(
            model_name="periodicasyncjob",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)s_jobs",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="periodicasyncjob",
            name="program",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="program.program",
            ),
        ),
        migrations.CreateModel(
            name="PeriodicAsyncRetryJob",
            fields=[],
            options={
                "verbose_name": "Periodic Retry Asynchronous Job",
                "verbose_name_plural": "Periodic Retry Asynchronous Jobs",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.periodicasyncjob",),
        ),
        migrations.AddField(
            model_name="flexibleattribute",
            name="pdu_data",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="flex_field",
                to="core.periodicfielddata",
            ),
        ),
        migrations.AddField(
            model_name="storagefile",
            name="business_area",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.businessarea",
            ),
        ),
        migrations.AddField(
            model_name="storagefile",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created by",
            ),
        ),
        migrations.AddField(
            model_name="xlsxkobotemplate",
            name="uploaded_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="asyncjob",
            index=models.Index(
                fields=["content_type", "object_id", "job_name"],
                name="core_asyncj_content_4eb670_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="asyncjob",
            index=hope.models.utils.LongNameIndex(fields=["object_id"], name="core_asyncjob_object_id_ab271347"),
        ),
        migrations.AddIndex(
            model_name="asyncjob",
            index=hope.models.utils.LongNameIndex(
                fields=["object_id"],
                name="core_asyncjob_object_id_ab271347_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="asyncjob",
            index=hope.models.utils.LongNameIndex(fields=["job_name"], name="core_asyncjob_job_name_26a164d8"),
        ),
        migrations.AddIndex(
            model_name="asyncjob",
            index=hope.models.utils.LongNameIndex(
                fields=["job_name"],
                name="core_asyncjob_job_name_26a164d8_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="businessarea",
            index=models.Index(fields=["active"], name="idx_ba_active"),
        ),
        migrations.AddIndex(
            model_name="businessarea",
            index=models.Index(fields=["slug", "active"], name="idx_ba_slug_active"),
        ),
        migrations.AddIndex(
            model_name="businessarea",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="core_businessarea_created_at_a213ff21"),
        ),
        migrations.AddIndex(
            model_name="businessarea",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="core_businessarea_updated_at_84b3ece5"),
        ),
        migrations.AddIndex(
            model_name="flexibleattributechoice",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="core_flexibleattributechoice_created_at_73c2246e",
            ),
        ),
        migrations.AddIndex(
            model_name="flexibleattributechoice",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="core_flexibleattributechoice_updated_at_466be573",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="flexibleattributechoice",
            unique_together={("list_name", "name")},
        ),
        migrations.AddIndex(
            model_name="flexibleattributegroup",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="core_flexibleattributegroup_created_at_2c428173",
            ),
        ),
        migrations.AddIndex(
            model_name="flexibleattributegroup",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="core_flexibleattributegroup_updated_at_cb04253b",
            ),
        ),
        migrations.AddIndex(
            model_name="flexibleattributegroup",
            index=models.Index(fields=["tree_id", "lft"], name="core_flexibleattributegroudd5f"),
        ),
        migrations.AddConstraint(
            model_name="datacollectingtype",
            constraint=models.UniqueConstraint(fields=("label", "code"), name="unique_label_code_data_collecting_type"),
        ),
        migrations.AddIndex(
            model_name="periodicasyncjob",
            index=models.Index(
                fields=["content_type", "object_id", "job_name"],
                name="core_period_content_22b5c0_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="periodicasyncjob",
            index=hope.models.utils.LongNameIndex(
                fields=["object_id"], name="core_periodicasyncjob_object_id_76f19a56"
            ),
        ),
        migrations.AddIndex(
            model_name="periodicasyncjob",
            index=hope.models.utils.LongNameIndex(
                fields=["object_id"],
                name="core_periodicasyncjob_object_id_76f19a56_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="periodicasyncjob",
            index=hope.models.utils.LongNameIndex(fields=["job_name"], name="core_periodicasyncjob_job_name_b168ae1a"),
        ),
        migrations.AddIndex(
            model_name="periodicasyncjob",
            index=hope.models.utils.LongNameIndex(
                fields=["job_name"],
                name="core_periodicasyncjob_job_name_b168ae1a_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="flexibleattribute",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="core_flexibleattribute_created_at_e15acdcb"
            ),
        ),
        migrations.AddIndex(
            model_name="flexibleattribute",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="core_flexibleattribute_updated_at_343b54a3"
            ),
        ),
        migrations.AddConstraint(
            model_name="flexibleattribute",
            constraint=models.UniqueConstraint(fields=("name", "program"), name="unique_name_program"),
        ),
        migrations.AddConstraint(
            model_name="flexibleattribute",
            constraint=models.UniqueConstraint(
                condition=models.Q(("program__isnull", True)),
                fields=("name",),
                name="unique_name_without_program",
            ),
        ),
        migrations.AddIndex(
            model_name="xlsxkobotemplate",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="core_xlsxkobotemplate_created_at_01750a92"
            ),
        ),
        migrations.AddIndex(
            model_name="xlsxkobotemplate",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="core_xlsxkobotemplate_updated_at_403ef208"
            ),
        ),
        # Each new business area gets its own sequences; the unicef_id triggers on payment plans, payments
        # and programme cycles draw from them.
        migrations.RunSQL(
            sql=[
                """CREATE OR REPLACE FUNCTION payment_plan_business_area_seq()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
            begin
                execute format('create sequence if not exists payment_plan_business_area_seq_%s', translate(NEW.id::text, '-','_'));
                return NEW;
            end
            $function$""",
                "CREATE TRIGGER payment_plan_business_area_seq AFTER INSERT ON core_businessarea FOR EACH ROW EXECUTE FUNCTION payment_plan_business_area_seq()",
                """CREATE OR REPLACE FUNCTION payment_business_area_seq()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
            begin
                execute format('create sequence if not exists payment_business_area_seq_%s', translate(NEW.id::text, '-','_'));
                return NEW;
            end
            $function$""",
                "CREATE TRIGGER payment_business_area_seq AFTER INSERT ON core_businessarea FOR EACH ROW EXECUTE FUNCTION payment_business_area_seq()",
                """CREATE OR REPLACE FUNCTION program_cycle_business_area_seq()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
                BEGIN
                    EXECUTE format('CREATE SEQUENCE IF NOT EXISTS program_cycle_business_area_seq_%s', translate(NEW.id::text, '-', '_'));
                    RETURN NEW;
                END
                $function$""",
                "CREATE TRIGGER program_cycle_business_area_seq AFTER INSERT ON core_businessarea FOR EACH ROW EXECUTE FUNCTION program_cycle_business_area_seq()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # django-mptt declares a (tree_id, lft) index on the models, but no existing database has it:
        # the replaced history added it to the migration state only.
        RunSQLAfterDeferred(
            sql=[
                "DROP INDEX IF EXISTS core_flexibleattributegroudd5f",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunPython(seed_reference_data, migrations.RunPython.noop),
    ]
