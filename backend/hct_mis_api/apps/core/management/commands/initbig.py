from django.core.management import BaseCommand, call_command
from django.db import connections

from hct_mis_api.apps.payment.fixtures import generate_real_cash_plans
from hct_mis_api.apps.registration_datahub.management.commands.fix_unicef_id_imported_individuals_and_households import (
    update_mis_unicef_id_individual_and_household,
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--scale",
            action="store",
            default=1.0,
        )

    def handle(self, *args, **options):
        print("Creating fake data")
        print(options["scale"])
