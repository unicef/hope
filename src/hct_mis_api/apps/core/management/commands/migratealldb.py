from typing import Any

import django.db.utils
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

GREEN = "\033[92m"


class Command(BaseCommand):
    help = "Migrate all databases specified in settings"

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            self.stdout.write(self.style.SUCCESS("Starting migration"))
        except django.db.utils.ProgrammingError:
            pass
        finally:
            for db in settings.DATABASES:
                self.stdout.write(self.style.WARNING(f"Migrating {db} database"))
                if db == "read_only":
                    self.stdout.write(self.style.WARNING(f"Migrating {db} database"))
                else:
                    call_command("migrate", database=db)
