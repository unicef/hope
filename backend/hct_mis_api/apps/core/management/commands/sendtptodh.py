from django.core.management.base import BaseCommand

from mis_datahub.tasks.send_tp_to_datahub import SendTPToDatahubTask

GREEN = "\033[92m"


class Command(BaseCommand):
    help = "Migrate all databases specified in settings"

    def handle(self, *args, **options):
        SendTPToDatahubTask().execute()
