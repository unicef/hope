import subprocess

from django.core.management import call_command
from django.core.management.commands import makemigrations


class Command(makemigrations.Command):
    def handle(self, *args, **options):
        call_command(
            "reset_db",
            "--noinput",
            "--close-sessions",
        )
        call_command(
            "reset_db",
            "--noinput",
            "--close-sessions",
            router="cash_assist_datahub_ca",
        )
        call_command(
            "reset_db",
            "--noinput",
            "--close-sessions",
            router="cash_assist_datahub_mis",
        )
        call_command(
            "reset_db",
            "--noinput",
            "--close-sessions",
            router="cash_assist_datahub_erp",
        )
        call_command(
            "reset_db",
            "--noinput",
            "--close-sessions",
            router="registration_datahub",
        )
        subprocess.call(["./create_schemas.sh"])
        call_command("migratealldb")
        call_command("loadbusinessareas")
        call_command("loadflexfieldsattributes")
        call_command("generatedocumenttypes")
        call_command("search_index", "--rebuild", "-f")
        call_command("generateroles")
        call_command("loaddata", "hct_mis_api/apps/account/fixtures/superuser.json")
