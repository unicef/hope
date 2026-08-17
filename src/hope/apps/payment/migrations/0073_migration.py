# Generated manually

from django.db import migrations


def migrate_preparing_to_open(apps, schema_editor):  # pragma no cover
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlan.objects.filter(status="PREPARING").update(status="OPEN")


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0072_migration"),
    ]

    operations = [
        migrations.RunPython(migrate_preparing_to_open, migrations.RunPython.noop),
    ]
