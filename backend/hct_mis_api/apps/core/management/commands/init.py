import subprocess

from django.core.management import call_command
from django.core.management.commands import makemigrations


class Command(makemigrations.Command):
    def handle(self, *args, **options):
        call_command("initempty")
        call_command("generatefixtures", "--noinput", flush=False)
