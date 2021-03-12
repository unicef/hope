import subprocess

from django.core.management import call_command, BaseCommand
from django.db import connections

from hct_mis_api.apps.core.management.sql import sql_drop_tables


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("collectstatic", interactive=False)
        call_command("migratealldb")
        call_command("search_index", "--rebuild", "-f")
        call_command("generateroles")
