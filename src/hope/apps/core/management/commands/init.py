from typing import Any

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        call_command("initempty")
        call_command("generatefixtures", "--noinput")
