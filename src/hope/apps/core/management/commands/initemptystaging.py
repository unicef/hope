from typing import Any

from django.core.management import BaseCommand, call_command
from extras.test_utils.factories.account import create_superuser


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        call_command("dropalldb")
        call_command("migrate")
        call_command("loadbusinessareas")
        call_command("generatedocumenttypes")
        call_command("search_index", "--rebuild", "-f")
        call_command("generateroles")
        create_superuser()
        call_command("loadcountries")
        call_command("loadcountrycodes")
