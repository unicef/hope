import subprocess

from django.core.management import call_command
from django.core.management.commands import makemigrations

from account.models import Role


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
        call_command("generatefixtures", "--noinput", flush=False)
        guest_role = Role()
        # TODO: add permissions later when all are done
        guest_role.permissions = []
        guest_role.name = "Guest"
        guest_role.save()
