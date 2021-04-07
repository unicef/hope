from django.conf import settings
from django.core.management import BaseCommand, call_command


def configure_beat():
    from django_celery_beat.models import (
        CrontabSchedule,
        IntervalSchedule,
        PeriodicTask,
    )

    hourly, __ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.HOURS)

    midnight, __ = CrontabSchedule.objects.get_or_create(minute=0, hour=0, timezone=settings.TIME_ZONE)

    minutes = {
        x: IntervalSchedule.objects.get_or_create(every=x, period=IntervalSchedule.MINUTES)[0] for x in [1, 20, 30]
    }

    tasks = [
        ("hct_mis_api.apps.sanction_list.celery_tasks.sync_sanction_list_task", midnight),
        ("hct_mis_api.apps.erp_datahub.celery_tasks.pull_from_erp_datahub_task", minutes[30]),
        ("hct_mis_api.apps.cash_assist_datahub.celery_tasks.pull_from_erp_dh_task", hourly),
        ("hct_mis_api.apps.payment.celery_tasks.get_sync_run_rapid_pro_task", minutes[20]),
    ]

    for interval, task in tasks:
        PeriodicTask.objects.get_or_create(task=task, defaults={"interval": interval, "name": task})


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("collectstatic", interactive=False)
        call_command("migratealldb")
        call_command("generateroles")
        configure_beat()
