from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("household", "0038_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="individual",
            name="deduplication_engine_reference_pk",
            field=models.CharField(
                blank=True,
                help_text="Reference pk used for biometric deduplication engine communication [sys]",
                max_length=255,
                null=True,
            ),
        ),
    ]
