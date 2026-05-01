from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0024_migration"),
        ("program", "0018_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="program",
            name="payment_plan_purposes",
            field=models.ManyToManyField(
                blank=True,
                help_text="Payment plan purposes available within program",
                related_name="programs",
                to="core.paymentplanpurpose",
            ),
        ),
    ]
