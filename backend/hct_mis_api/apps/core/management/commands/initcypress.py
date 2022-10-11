from datetime import timedelta
from django.utils import timezone

from uuid import UUID
from django.core.management import BaseCommand, call_command
from django.db import connections

from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.household.models import MALE
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.management.sql import sql_drop_tables
from hct_mis_api.apps.payment.fixtures import FinancialServiceProviderFactory
from hct_mis_api.apps.payment.models import GenericPayment
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory


def create_fsps():
    for delivery_mechanism in GenericPayment.DELIVERY_TYPE_CHOICE:
        dm = delivery_mechanism[0]
        FinancialServiceProviderFactory(
            name=f"Test FSP {dm}",
            delivery_mechanisms=[dm],
            distribution_limit=None,
        )


def create_household_with_individual(hh_pk, in_pk, address):
    now = timezone.now()
    delta_20_years = timedelta(days=365 * 20)
    afghanistan = BusinessArea.objects.get(name="Afghanistan")

    rdi = RegistrationDataImportFactory(
        data_source=RegistrationDataImport.XLS,
        business_area=afghanistan,
        number_of_households=1,
        number_of_individuals=1,
    )

    hh = Household(
        pk=hh_pk,
        first_registration_date=now,
        last_registration_date=now,
        business_area=afghanistan,
        address=address,
        registration_data_import=rdi,
    )

    ind = Individual.objects.create(
        pk=in_pk,
        birth_date=now - delta_20_years,
        first_registration_date=now,
        last_registration_date=now,
        business_area=afghanistan,
        sex=MALE,
    )

    hh.head_of_household = ind
    hh.save()

    ind.household = hh
    ind.save()


def initialize_data_for_targeting():
    create_household_with_individual(
        hh_pk=UUID("10000000-0000-0000-0000-000000000001"),
        in_pk=UUID("10000000-0000-0000-0001-000000000001"),
        address="TargettingVille",
    )

    program_pk = UUID("10000000-0000-0000-0002-000000000001")
    ProgramFactory(pk=program_pk, name="TargetingProgram", status=Program.ACTIVE)


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
        call_command(
            "loaddata", "hct_mis_api/apps/registration_datahub/fixtures/data.json", database="registration_datahub"
        )

        create_fsps()

        initialize_data_for_targeting()

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
