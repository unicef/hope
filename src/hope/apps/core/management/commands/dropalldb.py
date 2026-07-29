from contextlib import suppress

from django.core.management import BaseCommand

from hope.apps.core.management.sql import drop_databases


class Command(BaseCommand):
    def handle(self, *args: object, **options: object) -> None:
        with suppress(Exception):
            drop_databases()
