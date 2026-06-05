from itertools import islice
import uuid

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields

BATCH_SIZE = 2000


def _bulk_create_in_batches(model, objects_iter, ignore_conflicts=False):
    while batch := list(islice(objects_iter, BATCH_SIZE)):
        model.objects.bulk_create(batch, ignore_conflicts=ignore_conflicts)


def migrate_plan_type(apps, schema_editor):
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlan.objects.filter(is_follow_up=True).update(plan_type="FOLLOW_UP")


def create_default_purpose_and_backfill(apps, schema_editor):
    PaymentPlanPurpose = apps.get_model("payment", "PaymentPlanPurpose")  # noqa: N806
    BusinessArea = apps.get_model("core", "BusinessArea")  # noqa: N806
    Program = apps.get_model("program", "Program")  # noqa: N806
    PaymentPlan = apps.get_model("payment", "PaymentPlan")  # noqa: N806
    PaymentPlanGroup = apps.get_model("payment", "PaymentPlanGroup")  # noqa: N806

    ProgramThrough = Program.payment_plan_purposes.through  # noqa: N806
    PlanThrough = PaymentPlan.payment_plan_purposes.through  # noqa: N806

    for ba in BusinessArea.objects.all():
        default_purpose, _ = PaymentPlanPurpose.objects.get_or_create(name="Default Purpose", business_area_id=ba.id)

        program_ids_with_purpose = ProgramThrough.objects.filter(program__business_area_id=ba.id).values_list(
            "program_id", flat=True
        )
        _bulk_create_in_batches(
            ProgramThrough,
            (
                ProgramThrough(program_id=pk, paymentplanpurpose_id=default_purpose.id)
                for pk in Program.objects.filter(business_area_id=ba.id)
                .exclude(id__in=program_ids_with_purpose)
                .values_list("id", flat=True)
            ),
            ignore_conflicts=True,
        )

        plan_ids_with_purpose = PlanThrough.objects.filter(paymentplan__business_area_id=ba.id).values_list(
            "paymentplan_id", flat=True
        )
        _bulk_create_in_batches(
            PlanThrough,
            (
                PlanThrough(paymentplan_id=pk, paymentplanpurpose_id=default_purpose.id)
                for pk in PaymentPlan.objects.filter(business_area_id=ba.id)
                .exclude(id__in=plan_ids_with_purpose)
                .values_list("id", flat=True)
            ),
            ignore_conflicts=True,
        )

    ungrouped_pps = list(
        PaymentPlan.objects.filter(payment_plan_group__isnull=True).values_list("id", "name", "program_cycle_id")
    )
    _bulk_create_in_batches(
        PaymentPlanGroup,
        (PaymentPlanGroup(cycle_id=cycle_id, name=f"{pp_name} Group") for _, pp_name, cycle_id in ungrouped_pps),
        ignore_conflicts=True,
    )
    cycle_ids = {cycle_id for _, _, cycle_id in ungrouped_pps}
    group_lookup = {
        (g.cycle_id, g.name): g.id
        for g in PaymentPlanGroup.objects.filter(cycle_id__in=cycle_ids).only("id", "cycle_id", "name")
    }
    pps_to_update = [
        PaymentPlan(id=pp_id, payment_plan_group_id=group_lookup[cycle_id, f"{pp_name} Group"])
        for pp_id, pp_name, cycle_id in ungrouped_pps
        if (cycle_id, f"{pp_name} Group") in group_lookup
    ]
    PaymentPlan.objects.bulk_update(pps_to_update, ["payment_plan_group_id"], batch_size=BATCH_SIZE)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("core", "0028_migration"),
        ("payment", "0065_migration"),
        ("program", "0019_migration"),
    ]

    operations = [
        # --- PaymentPlanGroup ---
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
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("unicef_id", models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ("name", models.CharField(default="Default Group", max_length=255)),
                (
                    "cycle",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_plan_groups",
                        to="program.programcycle",
                        verbose_name="Programme Cycle",
                    ),
                ),
                (
                    "background_action_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("XLSX_EXPORTING", "Exporting XLSX file"),
                            ("XLSX_EXPORT_ERROR", "Export XLSX file Error"),
                            ("XLSX_IMPORTING_RECONCILIATION", "Importing Reconciliation XLSX file"),
                            ("XLSX_IMPORT_ERROR", "Import XLSX file Error"),
                        ],
                        db_index=True,
                        default=None,
                        help_text="Background Action Status for celery export/import task [sys]",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "delivery_import_file",
                    models.ForeignKey(
                        blank=True,
                        help_text="Uploaded reconciliation XLSX [sys]",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="core.filetemp",
                    ),
                ),
            ],
            options={
                "verbose_name": "Payment Plan Group",
                "app_label": "payment",
                "ordering": ["created_at"],
                "unique_together": {("cycle", "name")},
            },
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="payment_plan_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payment_plans",
                to="payment.paymentplangroup",
            ),
        ),
        migrations.RunSQL(
            sql="ALTER TABLE payment_paymentplangroup ADD unicef_id_index SERIAL",
            reverse_sql="ALTER TABLE payment_paymentplangroup DROP COLUMN unicef_id_index",
        ),
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION create_ppg_unicef_id() RETURNS trigger
                LANGUAGE plpgsql
                AS $$
            BEGIN
                NEW.unicef_id := format('PPG-%s', NEW.unicef_id_index);
                return NEW;
            END
            $$;

            CREATE TRIGGER create_ppg_unicef_id BEFORE INSERT ON payment_paymentplangroup FOR EACH ROW EXECUTE PROCEDURE create_ppg_unicef_id();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS create_ppg_unicef_id ON payment_paymentplangroup;
            DROP FUNCTION IF EXISTS create_ppg_unicef_id();
            """,
        ),
        # --- plan_type (replaces is_follow_up; final definition with all choices) ---
        migrations.AddField(
            model_name="paymentplan",
            name="plan_type",
            field=models.CharField(
                choices=[
                    ("REGULAR", "Regular"),
                    ("TOP_UP", "Top Up"),
                    ("FOLLOW_UP", "Follow Up"),
                    ("TOP_UP_AMENDMENT", "Top Up Amendment"),
                ],
                db_index=True,
                default="REGULAR",
                help_text="Payment Plan type [sys]",
                max_length=20,
            ),
        ),
        migrations.RunPython(migrate_plan_type, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="paymentplan",
            name="is_follow_up",
        ),
        # --- backfill purposes + assign all plans to groups ---
        migrations.RunPython(
            create_default_purpose_and_backfill,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="paymentplan",
            name="payment_plan_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payment_plans",
                to="payment.paymentplangroup",
            ),
        ),
        # --- source_payment_plan related_name rename ---
        migrations.AlterField(
            model_name="paymentplan",
            name="source_payment_plan",
            field=models.ForeignKey(
                blank=True,
                help_text="Source Payment Plan (applicable for follow-up and top-up Payment Plans)",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="child_plans",
                to="payment.paymentplan",
            ),
        ),
        # --- rename export_file_per_fsp → export_file_delivery ---
        migrations.RenameField(
            model_name="paymentplan",
            old_name="export_file_per_fsp",
            new_name="export_file_delivery",
        ),
        migrations.AlterField(
            model_name="paymentplan",
            name="export_file_delivery",
            field=models.ForeignKey(
                blank=True,
                help_text="Export File Delivery",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        # --- export_tag ---
        migrations.AddField(
            model_name="paymentplan",
            name="export_tag",
            field=models.PositiveSmallIntegerField(
                blank=True,
                db_index=True,
                help_text="Group delivery export batch number; set when the plan is included in a group export [sys]",
                null=True,
            ),
        ),
    ]
