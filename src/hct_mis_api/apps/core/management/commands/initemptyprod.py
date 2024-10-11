from typing import Any

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        call_command("migratealldb")
        call_command("loadbusinessareas")
        call_command("generatedocumenttypes")
        call_command("generateroles")
        call_command("loadcountries")
        call_command("loadcountrycodes")
