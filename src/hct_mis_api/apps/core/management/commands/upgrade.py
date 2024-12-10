from typing import Any

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        call_command("migratealldb")
        call_command("collectstatic", "--no-default-ignore", interactive=False)
        call_command("generateroles")
        from adminactions.perms import create_extra_permissions

        create_extra_permissions()
