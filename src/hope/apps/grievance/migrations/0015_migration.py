from django.db import migrations, models

import hope.apps.grievance.constants


class Migration(migrations.Migration):
    dependencies = [
        ("grievance", "0014_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="grievanceticket",
            name="source",
            field=models.IntegerField(
                blank=True,
                choices=hope.apps.grievance.constants.get_source_choices,
                help_text="Submission channel; empty for system-generated tickets.",
                null=True,
                verbose_name="Source",
            ),
        ),
    ]
