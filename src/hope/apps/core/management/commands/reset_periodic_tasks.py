from typing import Any

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask


class Command(BaseCommand):
    help = "Delete all django-celery-beat PeriodicTask rows so Celery beat can recreate them from TASKS_SCHEDULES."

    def handle(self, *args: Any, **options: Any) -> None:
        deleted_count, _ = PeriodicTask.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} PeriodicTask rows."))
        self.stdout.write("Restart celery-beat to recreate tasks from TASKS_SCHEDULES.")
