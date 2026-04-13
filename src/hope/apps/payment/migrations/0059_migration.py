import logging

from django.db import migrations, models
import django.db.models.deletion

logger = logging.getLogger(__name__)


def populate_payment_plan_currency_fk(apps, schema_editor):
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    Currency = apps.get_model("core", "Currency")

    currency_map = dict(Currency.objects.values_list("code", "pk"))

    qs = PaymentPlan.objects.exclude(currency_old="").exclude(currency_old__isnull=True)
    for currency_code, pk_value in currency_map.items():
        qs.filter(currency_old=currency_code, currency__isnull=True).update(currency_id=pk_value)

    unmatched = qs.filter(currency__isnull=True).values_list("currency_old", flat=True).distinct()
    for code in unmatched:
        count = qs.filter(currency_old=code, currency__isnull=True).count()
        logger.warning("PaymentPlan: %d rows with unrecognized currency code '%s'", count, code)


def reverse_populate_payment_plan(apps, schema_editor):
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    Currency = apps.get_model("core", "Currency")

    currency_map = dict(Currency.objects.values_list("pk", "code"))

    for pk_value, currency_code in currency_map.items():
        PaymentPlan.objects.filter(currency_id=pk_value).update(currency_old=currency_code)


def populate_payment_currency_fk(apps, schema_editor):
    Payment = apps.get_model("payment", "Payment")
    Currency = apps.get_model("core", "Currency")

    currency_map = dict(Currency.objects.values_list("code", "pk"))

    qs = Payment.objects.exclude(currency_old="").exclude(currency_old__isnull=True)
    for currency_code, pk_value in currency_map.items():
        qs.filter(currency_old=currency_code, currency__isnull=True).update(currency_id=pk_value)

    unmatched = qs.filter(currency__isnull=True).values_list("currency_old", flat=True).distinct()
    for code in unmatched:
        count = qs.filter(currency_old=code, currency__isnull=True).count()
        logger.warning("Payment: %d rows with unrecognized currency code '%s'", count, code)


def reverse_populate_payment(apps, schema_editor):
    Payment = apps.get_model("payment", "Payment")
    Currency = apps.get_model("core", "Currency")

    currency_map = dict(Currency.objects.values_list("pk", "code"))

    for pk_value, currency_code in currency_map.items():
        Payment.objects.filter(currency_id=pk_value).update(currency_old=currency_code)


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0058_migration"),
        ("core", "0019_migration"),
    ]

    operations = [
        # PaymentPlan: CharField → FK
        migrations.RenameField(
            model_name="paymentplan",
            old_name="currency",
            new_name="currency_old",
        ),
        migrations.AlterField(
            model_name="paymentplan",
            name="currency_old",
            field=models.CharField(
                blank=True,
                help_text="Currency (legacy, pending removal)",
                max_length=5,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                help_text="Currency",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="payment_plans",
                to="core.currency",
            ),
        ),
        migrations.RunPython(populate_payment_plan_currency_fk, reverse_populate_payment_plan),
        # Payment: CharField → FK
        migrations.RenameField(
            model_name="payment",
            old_name="currency",
            new_name="currency_old",
        ),
        migrations.AddField(
            model_name="payment",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="payments",
                to="core.currency",
                help_text="Currency",
            ),
        ),
        migrations.RunPython(populate_payment_currency_fk, reverse_populate_payment),
    ]
