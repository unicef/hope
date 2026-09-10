# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("registration_data", "0016_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="registrationdataimport",
            name="program",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="registration_imports",
                to="program.program",
            ),
        ),
    ]
