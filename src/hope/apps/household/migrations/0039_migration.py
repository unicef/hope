from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("household", "0038_migration"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="individual",
            name="dedup_ref_pk_unique_in_program",
        ),
        migrations.AddConstraint(
            model_name="individual",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_removed", False), ("deduplication_engine_reference_pk__isnull", False))
                & ~models.Q(("deduplication_engine_reference_pk", "")),
                fields=("program", "deduplication_engine_reference_pk"),
                name="dedup_ref_pk_unique_in_program",
            ),
        ),
    ]
