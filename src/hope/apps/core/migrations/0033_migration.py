from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0032_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="businessarea",
            name="vision_integration_active",
            field=models.BooleanField(default=False),
        ),
    ]
