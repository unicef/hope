from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0062_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="payment",
            name="currency_old",
        ),
        migrations.RemoveField(
            model_name="paymentplan",
            name="currency_old",
        ),
    ]
