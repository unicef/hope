# Generated manually

from django.db import migrations


def migrate_processing_to_draft(apps, schema_editor):  # pragma no cover
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlan.objects.filter(status="PROCESSING").update(status="DRAFT")


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0074_migration"),
    ]

    operations = [
        migrations.RunPython(migrate_processing_to_draft, migrations.RunPython.noop),
    ]
