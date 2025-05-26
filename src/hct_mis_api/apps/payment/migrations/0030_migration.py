from django.db import migrations, models


def migrate_payments_delivery_mechanism(apps, schema_editor):  # pragma: no cover
    Payment = apps.get_model("payment", "Payment")
    DeliveryMechanism = apps.get_model("payment", "DeliveryMechanism")
    dm_cash_by_fsp = DeliveryMechanism.objects.filter(code="cash_by_fsp").first()
    dm_cash = DeliveryMechanism.objects.filter(code="cash").first()
    if dm_cash_by_fsp:
        Payment.objects.filter(delivery_type_id=dm_cash.id).update(delivery_type_id=dm_cash_by_fsp.id)


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0029_migration'),
    ]

    operations = [
        migrations.RunPython(migrate_payments_delivery_mechanism, reverse_code=migrations.RunPython.noop),
    ]
