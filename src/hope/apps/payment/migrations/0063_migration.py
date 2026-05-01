from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0024_migration"),
        ("payment", "0062_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentplan",
            name="payment_plan_purposes",
            field=models.ManyToManyField(
                blank=True,
                help_text="Payment plan purposes",
                related_name="payment_plans",
                to="core.paymentplanpurpose",
            ),
        ),
    ]
