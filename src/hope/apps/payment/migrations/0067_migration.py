import uuid

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0028_migration"),
        ("payment", "0066_migration"),
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
        # --- plan_type (added alongside is_follow_up; backfill + removal happen in 0069/0070) ---
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
