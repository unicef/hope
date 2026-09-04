from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

NOTIFICATION_JOB_NAMES = (
    "send_payment_notification_emails_async_task",
    "send_pdu_online_edit_notification_emails_async_task",
)


def backfill_notification_action_dates(
    apps: Apps,
    _schema_editor: BaseDatabaseSchemaEditor | None,
) -> None:
    AsyncJob = apps.get_model("core", "AsyncJob")
    jobs_to_update = []
    legacy_jobs = (
        AsyncJob.objects.filter(
            job_name__in=NOTIFICATION_JOB_NAMES,
            config__has_key="action_date_formatted",
        )
        .exclude(config__has_key="action_date")
        .only("config", "datetime_created")
    )

    for job in legacy_jobs.iterator(chunk_size=500):
        job_config = dict(job.config)
        job_config["action_date"] = job.datetime_created.isoformat()
        job.config = job_config
        jobs_to_update.append(job)

    AsyncJob.objects.bulk_update(jobs_to_update, ("config",), batch_size=500)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0034_migration"),
    ]

    operations = [
        migrations.RunPython(backfill_notification_action_dates, migrations.RunPython.noop),
    ]
