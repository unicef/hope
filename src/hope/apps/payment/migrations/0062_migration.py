from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0061_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentplan",
            name="use_payment_gateway",
            field=models.BooleanField(
                default=False,
                help_text="Send this payment plan through the payment gateway regardless of the FSP communication channel",
            ),
        ),
    ]
