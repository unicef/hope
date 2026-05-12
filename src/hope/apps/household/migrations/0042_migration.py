from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("household", "0041_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="household",
            name="currency_old",
        ),
    ]
