from django.core.management import BaseCommand, call_command
from django.db import connections

from hct_mis_api.apps.core.management.sql import sql_drop_tables


class Command(BaseCommand):
    def handle(self, *args, **options):
        for connection_name in connections:
            if connection_name == "read_only":
                continue
            connection = connections[connection_name]
            with connection.cursor() as cursor:
                sql = sql_drop_tables(connection)
                if not sql:
                    continue
                print(sql)
                cursor.execute(sql)

        # subprocess.call(["./create_schemas.sh"])
        call_command("migratealldb")
        call_command("loadbusinessareas")
        # call_command("loadflexfieldsattributes")
        call_command("generatedocumenttypes")
        call_command("search_index", "--rebuild", "-f")
        call_command("generateroles")
        call_command("loaddata", "hct_mis_api/apps/account/fixtures/superuser.json")
        call_command("loadcountries")
        call_command("loadcountrycodes")
