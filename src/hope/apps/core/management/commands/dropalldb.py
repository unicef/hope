from contextlib import suppress
from typing import Any

from django.core.management import BaseCommand

from hope.apps.core.management.sql import drop_databases


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        with suppress(Exception):
            drop_databases()
