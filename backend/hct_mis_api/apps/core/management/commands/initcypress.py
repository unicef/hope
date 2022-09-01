from django.core.management import BaseCommand, call_command
from django.db import connections

from hct_mis_api.apps.core.management.sql import sql_drop_tables


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-drop",
            action="store_true",
            default=False,
            help="Skip migrating - just reload the data",
        )

    def handle(self, *args, **options):
        if options["skip_drop"] is False:
            self._drop_databases()
            call_command("migratealldb")

        call_command("flush", "--noinput")
        call_command("flush", "--noinput", database="cash_assist_datahub_mis")
        call_command("flush", "--noinput", database="cash_assist_datahub_ca")
        call_command("flush", "--noinput", database="cash_assist_datahub_erp")
        call_command("flush", "--noinput", database="registration_datahub")

        call_command("loaddata", "hct_mis_api/apps/core/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/account/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/geo/fixtures/data.json")
        call_command(
            "loaddata", "hct_mis_api/apps/registration_datahub/fixtures/data.json", database="registration_datahub"
        )

        call_command("search_index", "--rebuild", "-f")

    def _drop_databases(self):
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
