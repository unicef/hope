from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("household", "0039_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="individual",
            name="country_workspace_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text=(
                    "Primary key of the Individual on the originating Country Workspace system. "
                    "Used as the reference key when communicating with the Deduplication Engine."
                ),
                max_length=150,
                null=True,
            ),
        ),
    ]
