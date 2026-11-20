from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vision", "0006_migration"),
        ("payment", "0088_migration"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(
                    model_name="fundscommitmentheader", old_name="payment_plan_groups", new_name="payment_plans"
                ),
                migrations.AlterField(
                    model_name="fundscommitmentheader",
                    name="payment_plans",
                    field=models.ManyToManyField(
                        blank=True,
                        db_table="vision_fundscommitmentheader_payment_plan_groups",
                        related_name="funds_commitment_headers",
                        to="payment.paymentplan",
                    ),
                ),
            ],
        ),
    ]
