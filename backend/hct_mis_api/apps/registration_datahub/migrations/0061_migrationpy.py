from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration_datahub", "0060_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="importedhousehold",
            name="mis_unicef_id",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="importedindividual",
            name="mis_unicef_id",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
