from django.core.management.commands import makemigrations

from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import (
    PullFromDatahubTask,
)


class Command(makemigrations.Command):
    def handle(self, *args, **options):
        print(PullFromDatahubTask().execute())
