from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("household", "0039_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="individual",
            name="country_workspace_id",
            field=models.BigIntegerField(
                blank=True,
                db_index=True,
                help_text=(
                    "Primary key of the Individual on the originating Country Workspace system. "
                    "Used as the reference key when communicating with the Deduplication Engine."
                ),
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="individual",
            constraint=models.UniqueConstraint(
                condition=models.Q(("country_workspace_id__isnull", False)),
                fields=("country_workspace_id",),
                name="uniq_country_workspace_id",
            ),
        ),
    ]
