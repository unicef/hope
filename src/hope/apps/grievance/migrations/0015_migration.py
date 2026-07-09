from django.db import migrations, models

import hope.apps.grievance.constants


class Migration(migrations.Migration):
    dependencies = [
        ("grievance", "0014_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="grievanceticket",
            name="submission_channel",
            field=models.IntegerField(
                blank=True,
                choices=hope.apps.grievance.constants.get_submission_channel_choices,
                help_text="Submission channel; empty for system-generated tickets.",
                null=True,
                verbose_name="Submission Channel",
            ),
        ),
    ]
