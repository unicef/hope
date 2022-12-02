# Hand-written

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("household", "0127_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="individual",
            name="phone_no_alternative_valid",
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name="individual",
            name="phone_no_valid",
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
