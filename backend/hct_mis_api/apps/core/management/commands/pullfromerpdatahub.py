from django.core.management.commands import makemigrations

from hct_mis_api.apps.erp_datahub.tasks.pull_from_erp_datahub import (
    PullFromErpDatahubTask,
)


class Command(makemigrations.Command):
    def handle(self, *args, **options) -> None:
        PullFromErpDatahubTask().execute()
