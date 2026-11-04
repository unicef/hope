from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("targeting", "0013_migration"),
        ("payment", "0087_migration"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(
                    model_name="targetingcriteriarule", old_name="payment_plan", new_name="payment_list"
                ),
                migrations.AlterField(
                    model_name="targetingcriteriarule",
                    name="payment_list",
                    field=models.ForeignKey(
                        db_column="payment_plan_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rules",
                        to="payment.paymentlist",
                    ),
                ),
            ],
        ),
    ]
