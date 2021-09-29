import subprocess

from django.core.management import BaseCommand, call_command
from django.db import connections

from hct_mis_api.apps.core.management.sql import sql_drop_tables


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("migratealldb")
        call_command("loadbusinessareas")
        call_command("generatedocumenttypes")
        call_command("generateroles")
        call_command("loadcountries")
        call_command("loadcountrycodes")
