import uuid

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0028_migration"),
        ("payment", "0063_migration"),
        ("program", "0018_migration"),
    ]

    operations = [
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
                        ],
                        db_index=True,
                        default=None,
                        help_text="Background Action Status for celery task [sys]",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "export_file",
                    models.ForeignKey(
                        blank=True,
                        help_text="Merged XLSX export file [sys]",
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
        ),
    ]
