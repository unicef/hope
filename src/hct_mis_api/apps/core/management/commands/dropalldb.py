from typing import Any

from django.core.management import BaseCommand

from hct_mis_api.apps.core.management.sql import drop_databases
import contextlib


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        with contextlib.suppress(Exception):
            drop_databases()
