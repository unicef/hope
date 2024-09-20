from typing import Any

import django.db.utils
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from hct_mis_api.apps.core.models import MigrationStatus

GREEN = "\033[92m"


class Command(BaseCommand):
    help = "Migrate all databases specified in settings"

    def handle(self, *args: Any, **options: Any) -> None:
        migration = None
        try:
            migration = MigrationStatus.objects.get_or_create(is_running=True)[0]
            self.stdout.write(self.style.SUCCESS("Starting migration"))
        except django.db.utils.ProgrammingError:
            pass
        finally:
            try:
                for db in settings.DATABASES:
                    self.stdout.write(self.style.WARNING(f"Migrating {db} database"))
                    if db == "read_only":
                        self.stdout.write(self.style.WARNING(f"Migrating {db} database"))
                    else:
                        call_command("migrate", database=db)
            finally:
                if migration:
                    self.stdout.write(self.style.SUCCESS("Migration complete"))
                    migration.delete()
