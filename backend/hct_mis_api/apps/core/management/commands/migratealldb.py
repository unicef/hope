from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

GREEN = "\033[92m"


class Command(BaseCommand):
    help = "Migrate all databases specified in settings"

    def handle(self, *args, **options):
        for db in settings.DATABASES:
            self.stdout.write(self.style.WARNING(f"Migrating {db} database"))
            call_command("migrate", database=db)
