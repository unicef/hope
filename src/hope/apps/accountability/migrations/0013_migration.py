from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accountability", "0012_migration"),
        ("payment", "0088_migration"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(model_name="message", old_name="payment_plan", new_name="payment_list"),
                migrations.RenameField(model_name="survey", old_name="payment_plan", new_name="payment_list"),
                migrations.AlterField(
                    model_name="message",
                    name="payment_list",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="payment_plan_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="messages",
                        to="payment.paymentlist",
                    ),
                ),
                migrations.AlterField(
                    model_name="survey",
                    name="payment_list",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="payment_plan_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="surveys",
                        to="payment.paymentlist",
                    ),
                ),
            ],
        ),
    ]
