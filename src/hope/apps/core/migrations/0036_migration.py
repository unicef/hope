from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

# The per-ticket grievance reminder task is gone - its overdue and sensitive reminders are now
# sections of the daily digest. Beat raises KeyError on every tick for a row still pointing at it.
RETIRED_TASK = "hope.apps.grievance.celery_tasks.periodic_grievances_notifications_async_task"


def drop_retired_grievance_reminder_task(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(task=RETIRED_TASK).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0035_migration"),
        ("django_celery_beat", "0019_alter_periodictasks_options"),
    ]

    operations = [
        migrations.RunPython(drop_retired_grievance_reminder_task, migrations.RunPython.noop),
    ]
