from django.core.management import BaseCommand, call_command
from django.db import connections

from hct_mis_api.apps.core.management.sql import sql_drop_tables
from hct_mis_api.apps.payment.fixtures import (
    generate_payment_plan,
    generate_real_cash_plans,
    generate_real_payment_plans,
)
from hct_mis_api.apps.registration_datahub.management.commands.fix_unicef_id_imported_individuals_and_households import (
    update_mis_unicef_id_individual_and_household,
)


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

        call_command("loaddata", "hct_mis_api/apps/geo/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/core/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/account/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/registration_data/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/household/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/grievance/fixtures/data.json")

        call_command(
            "loaddata", "hct_mis_api/apps/registration_datahub/fixtures/data.json", database="registration_datahub"
        )
        call_command(
            "loaddata", "hct_mis_api/apps/registration_datahub/fixtures/diiadata.json", database="registration_datahub"
        )
        call_command("loaddata", "hct_mis_api/apps/steficon/fixtures/data.json")

        call_command("search_index", "--rebuild", "-f")
        generate_real_cash_plans()
        generate_real_payment_plans()
        update_mis_unicef_id_individual_and_household()
        generate_payment_plan()

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
