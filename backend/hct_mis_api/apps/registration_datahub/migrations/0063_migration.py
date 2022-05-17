from django.db import migrations


def update_status(apps, schema_editor):
    Record = apps.get_model("registration_datahub", "Record")

    Record.objects.filter(registration_data_import__isnull=False).update(status="IMPORTED")


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0062_migration'),
    ]

    operations = [
        migrations.RunPython(update_status, migrations.RunPython.noop)
    ]
