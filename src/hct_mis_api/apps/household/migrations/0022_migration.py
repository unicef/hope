# Generated by Django 3.2.25 on 2025-07-17 09:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("household", "0021_migration"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="household",
            name="identification_key_unique_constraint",
        ),
        migrations.AddField(
            model_name="individual",
            name="identification_key",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Key used to identify Collisions in the system",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="household",
            name="identification_key",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Key used to identify Collisions in the system",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="household",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("is_removed", False), ("identification_key__isnull", False), ("rdi_merge_status", "MERGED")
                ),
                fields=("identification_key", "program"),
                name="identification_key_unique_constraint",
            ),
        ),
        migrations.AddConstraint(
            model_name="individual",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("is_removed", False), ("identification_key__isnull", False), ("rdi_merge_status", "MERGED")
                ),
                fields=("identification_key", "program"),
                name="identification_key_ind_unique_constraint",
            ),
        ),
    ]
