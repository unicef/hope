from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("program", "0025_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="beneficiarygroup",
            name="master_detail",
        ),
    ]
