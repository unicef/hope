from django.core.management.commands import makemigrations

from cash_assist_datahub.tasks.pull_from_datahub import PullFromDatahubTask


class Command(makemigrations.Command):
    def handle(self, *args, **options):
        PullFromDatahubTask().execute()
