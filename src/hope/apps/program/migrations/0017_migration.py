from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("program", "0016_migration"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="program",
            name="unique_for_business_area_and_slug_if_not_removed",
        ),
        migrations.RemoveConstraint(
            model_name="program",
            name="unique_for_business_area_and_programme_code_if_not_removed",
        ),
        migrations.RemoveField(
            model_name="program",
            name="programme_code",
        ),
        migrations.RenameField(
            model_name="program",
            old_name="slug",
            new_name="code",
        ),
        migrations.AlterField(
            model_name="program",
            name="code",
            field=models.CharField(db_index=True, help_text="Program code", max_length=4),
        ),
        migrations.AddConstraint(
            model_name="program",
            constraint=models.UniqueConstraint(
                condition=models.Q(is_removed=False),
                fields=["business_area", "code"],
                name="unique_for_business_area_and_code_if_not_removed",
            ),
        ),
    ]
