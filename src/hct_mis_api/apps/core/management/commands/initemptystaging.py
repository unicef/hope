from typing import Any

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        call_command("dropalldb")
        call_command("migrate")
        call_command("loadbusinessareas")
        call_command("generatedocumenttypes")
        call_command("search_index", "--rebuild", "-f")
        call_command("generateroles")
        call_command("loaddata", "hct_mis_api/apps/account/fixtures/superuser.json")
        call_command("loadcountries")
        call_command("loadcountrycodes")
