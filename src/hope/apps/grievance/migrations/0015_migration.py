from django.db import migrations, models

import hope.apps.grievance.constants

# System-generated categories (Needs Adjudication, Payment Verification, System Flagging).
SYSTEM_CATEGORY_CODES = [8, 1, 9]
SUBMISSION_CHANNEL_HOPE = 5


def set_hope_channel_for_system_tickets(apps, schema_editor):
    GrievanceTicket = apps.get_model("grievance", "GrievanceTicket")
    GrievanceTicket.objects.filter(category__in=SYSTEM_CATEGORY_CODES, submission_channel__isnull=True).update(
        submission_channel=SUBMISSION_CHANNEL_HOPE
    )


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
        migrations.RunPython(set_hope_channel_for_system_tickets, migrations.RunPython.noop),
    ]
