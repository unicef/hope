import time

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import OperationalError, connections

from hct_mis_api.apps.payment.fixtures import generate_real_cash_plans
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
        db_connection = connections["default"]
        connected = False

        while not connected:
            try:
                db_connection.cursor()
                time.sleep(0.5)
            except OperationalError:
                connected = False
            else:
                connected = True

        if options["skip_drop"] is False:
            call_command("dropalldb")
            call_command("migratealldb")

        call_command("flush", "--noinput")
        call_command("flush", "--noinput", database="cash_assist_datahub_mis")
        call_command("flush", "--noinput", database="cash_assist_datahub_ca")
        call_command("flush", "--noinput", database="cash_assist_datahub_erp")
        call_command("flush", "--noinput", database="registration_datahub")

        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/account/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/grievance/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/accountability/fixtures/data.json")

        call_command(
            "loaddata",
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/fixtures/data.json",
            database="registration_datahub",
        )
        call_command(
            "loaddata",
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/fixtures/diiadata.json",
            database="registration_datahub",
        )

        call_command("search_index", "--rebuild", "-f")
        generate_real_cash_plans()
        update_mis_unicef_id_individual_and_household()
