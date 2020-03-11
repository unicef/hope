from django.core.management.commands import makemigrations
from django.core.management import call_command


class Command(makemigrations.Command):
    def handle(self, *args, **options):
        call_command("reset_db", "--noinput", "--close-sessions")
        call_command("migratealldb")
        call_command("loadbusinessareas")
        call_command("generatefixtures")
