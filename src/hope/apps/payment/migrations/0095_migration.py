from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0094_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentplangroup",
            name="internal_data",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
