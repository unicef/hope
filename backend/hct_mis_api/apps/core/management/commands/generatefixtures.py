import multiprocessing
import string
import time
from random import choice

import factory.random
from django.core.management import BaseCommand

from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from core.models import BusinessArea
from household.fixtures import (
    EntitlementCardFactory,
    HouseholdFactory,
    IndividualFactory,
)
from household.models import Household
from payment.fixtures import PaymentRecordFactory
from program.fixtures import CashPlanFactory, ProgramFactory
from registration_data.fixtures import RegistrationDataImportFactory
from registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
    ImportedIndividualFactory,
    ImportedHouseholdFactory,
)
from targeting.fixtures import TargetPopulationFactory


class Command(BaseCommand):
    help = "Generate fixtures data for project"

    def add_arguments(self, parser):
        parser.add_argument(
            "--program",
            dest="programs_amount",
            const=10,
            default=10,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of program objects.",
        )

        parser.add_argument(
            "--cash-plan",
            dest="cash_plans_amount",
            const=10,
            default=10,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of cash plans for one program.",
        )

        parser.add_argument(
            "--payment-record",
            dest="payment_record_amount",
            const=10,
            default=10,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of payment records assigned to "
            "household and cash plan.",
        )

    @staticmethod
    def _generate_program_with_dependencies(args_tuple):
        options, seed = args_tuple
        factory.random.reseed_random(seed)
        cash_plans_amount = options["cash_plans_amount"]
        payment_record_amount = options["payment_record_amount"]
        business_area = BusinessArea.objects.first()

        user = UserFactory()

        program = ProgramFactory(business_area=business_area)

        for _ in range(cash_plans_amount):
            cash_plan = CashPlanFactory(program=program, created_by=user)
            for _ in range(payment_record_amount):
                location = LocationFactory(business_area=business_area)

                registration_data_import = RegistrationDataImportFactory(
                    imported_by=user,
                )

                household = HouseholdFactory(
                    location=location,
                    registration_data_import_id=registration_data_import,
                )
                individuals = IndividualFactory.create_batch(
                    4,
                    household=household,
                    registration_data_import_id=registration_data_import,
                )
                household.head_of_household = individuals[0]
                household.representative = individuals[0]
                household.save()

                household.programs.add(program)

                target_population = TargetPopulationFactory(
                    households=household, created_by=user
                )
                PaymentRecordFactory(
                    cash_plan=cash_plan,
                    household=household,
                    target_population=target_population,
                )
                EntitlementCardFactory(household=household)

    def handle(self, *args, **options):
        start_time = time.time()
        programs_amount = options["programs_amount"]

        map_args = [
            (
                options,
                "".join(choice(string.ascii_lowercase) for _ in range(20)),
            )
            for _ in range(programs_amount)
        ]

        pool = multiprocessing.Pool(processes=7)
        pool.map(
            self._generate_program_with_dependencies, map_args,
        )
        pool.close()
        pool.join()

        registration_data_import_dth = RegistrationDataImportDatahubFactory()
        for _ in range(50):
            imported_household = ImportedHouseholdFactory(
                registration_data_import_id=registration_data_import_dth,
            )
            imported_individuals = ImportedIndividualFactory.create_batch(
                4,
                household=imported_household,
                registration_data_import_id=registration_data_import_dth,
            )
            imported_household.head_of_household = imported_individuals[0]
            imported_household.representative = imported_individuals[0]
            imported_household.save()

        # quick fix for households without payment_records
        Household.objects.filter(payment_records=None).delete()

        self.stdout.write(
            f"Generated fixtures in {(time.time() - start_time)} seconds"
        )
