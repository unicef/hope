from time import sleep
from typing import Any

from django.apps import apps
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        while not apps.ready:
            # Wait until the application started
            sleep(1)

        call_command("collectstatic", interactive=False)
        call_command("migratealldb")
        call_command("generateroles")
        from adminactions.perms import create_extra_permissions

        create_extra_permissions()

        from hct_mis_api.apps.power_query.defaults import create_defaults

        create_defaults()
