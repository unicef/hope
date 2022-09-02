from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0067_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="payment_plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="payment_items", to="payment.paymentplan"
            ),
        ),
        migrations.RenameField(
            model_name="payment",
            old_name="payment_plan",
            new_name="parent",
        ),
        migrations.AlterField(
            model_name="paymentrecord",
            name="cash_plan",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_items",
                to="payment.cashplan",
            ),
        ),
        migrations.RenameField(
            model_name="paymentrecord",
            old_name="cash_plan",
            new_name="parent",
        ),
        migrations.RemoveConstraint(
            model_name="payment",
            name="payment_plan_and_household",
        ),
        migrations.AddConstraint(
            model_name="payment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_removed", False)),
                fields=("parent", "household"),
                name="payment_plan_and_household",
            ),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='exchange_rate',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=14, null=True),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='exchange_rate',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=14, null=True),
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['unicef_id']},
        ),
    ]
