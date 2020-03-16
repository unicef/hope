import random
import time

from django.core.management import BaseCommand, call_command
from django.db import transaction

from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from core.models import BusinessArea
from household.fixtures import (
    EntitlementCardFactory,
    HouseholdFactory,
    IndividualFactory,
)
from payment.fixtures import PaymentRecordFactory
from program.fixtures import CashPlanFactory, ProgramFactory
from registration_data.fixtures import RegistrationDataImportFactory
from registration_data.models import RegistrationDataImport
from registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
    ImportedIndividualFactory,
    ImportedHouseholdFactory,
)
from targeting.fixtures import TargetPopulationFactory, TargetRuleFactory


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

        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Suppresses all user prompts.",
        )

    @staticmethod
    def _generate_program_with_dependencies(options):
        cash_plans_amount = options["cash_plans_amount"]
        payment_record_amount = options["payment_record_amount"]
        business_area = BusinessArea.objects.first()

        user = UserFactory()

        locations = LocationFactory.create_batch(
            3, business_area=business_area,
        )
        program = ProgramFactory(
            business_area=business_area, locations=locations,
        )

        for _ in range(cash_plans_amount):
            cash_plan = CashPlanFactory.build(
                program=program, created_by=user, target_population=None,
            )

            for _ in range(payment_record_amount):
                registration_data_import = RegistrationDataImportFactory(
                    imported_by=user,
                )

                household = HouseholdFactory(
                    location=random.choice(locations),
                    registration_data_import_id=registration_data_import,
                )
                individuals = IndividualFactory.create_batch(
                    household.family_size,
                    household=household,
                    registration_data_import_id=registration_data_import,
                )
                household.head_of_household = individuals[0]
                household.representative = individuals[0]
                household.save()

                household.programs.add(program)

                target_rules = TargetRuleFactory.create_batch(5)

                target_population = TargetPopulationFactory(
                    households=[household], created_by=user,
                )
                target_population.target_rules.add(*target_rules)

                cash_plan.target_population = target_population
                cash_plan.save()

                PaymentRecordFactory(
                    cash_plan=cash_plan,
                    household=household,
                    target_population=target_population,
                )
                EntitlementCardFactory(household=household)

    @transaction.atomic
    def handle(self, *args, **options):
        start_time = time.time()
        programs_amount = options["programs_amount"]

        business_areas = BusinessArea.objects.all().count()
        if not business_areas:
            if options["noinput"]:
                call_command("loadbusinessareas")
            else:
                self.stdout.write(
                    self.style.WARNING("BusinessAreas does not exist, ")
                )

                user_input = input("Type 'y' to generate, or 'n' to cancel: ")

                if user_input.upper() == "Y" or options["noinput"]:
                    call_command("loadbusinessareas")
                else:
                    self.stdout.write("Generation canceled")
                    return

        for _ in range(programs_amount):
            self._generate_program_with_dependencies(options)

        # Data imports generation
        data_imports_dth = RegistrationDataImportDatahubFactory.create_batch(
            5, hct_id=RegistrationDataImport.objects.all()[0].id
        )
        for data_import in data_imports_dth:
            for _ in range(50):
                imported_household = ImportedHouseholdFactory(
                    registration_data_import_id=data_import,
                )
                imported_individuals = ImportedIndividualFactory.create_batch(
                    imported_household.family_size,
                    household=imported_household,
                    registration_data_import_id=data_import,
                )
                imported_household.head_of_household = imported_individuals[0]
                imported_household.representative = imported_individuals[0]
                imported_household.save()

        self.stdout.write(
            f"Generated fixtures in {(time.time() - start_time)} seconds"
        )
