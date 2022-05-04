from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration_datahub", "0059_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="ignored",
            field=models.BooleanField(blank=True, db_index=True, default=False, null=True),
        ),
    ]
