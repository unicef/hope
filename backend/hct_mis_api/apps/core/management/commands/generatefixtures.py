import random
import time

from django.core.management import BaseCommand, call_command
from django.db import transaction

from account.fixtures import UserFactory
from core.fixtures import AdminAreaFactory, AdminAreaTypeFactory
from core.models import BusinessArea, AdminArea
from household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    EntitlementCardFactory,
    DocumentFactory,
    create_household,
)
from household.models import DocumentType
from payment.fixtures import PaymentRecordFactory
from program.fixtures import CashPlanFactory, ProgramFactory
from registration_data.fixtures import RegistrationDataImportFactory
from registration_data.models import RegistrationDataImport
from registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
    ImportedIndividualFactory,
    ImportedHouseholdFactory,
    create_imported_household,
)
from targeting.fixtures import (
    TargetPopulationFactory,
    TargetingCriteriaRuleFactory,
    TargetingCriteriaRuleFilterFactory,
    TargetingCriteriaFactory,
)


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
            "--flush",
            dest="flush",
            const=True,
            default=True,
            action="store",
            nargs="?",
            type=bool,
            help="Flush all tables in db.",
        )

        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Suppresses all user prompts.",
        )

    def _generate_admin_areas(self):
        business_area = BusinessArea.objects.first()
        state_area_type = AdminAreaTypeFactory(
            name="State", business_area=business_area, admin_level=1
        )
        province_area_type = AdminAreaTypeFactory(
            name="Province", business_area=business_area, admin_level=2
        )
        AdminAreaFactory.create_batch(
            6, admin_area_type=state_area_type,
        )
        AdminAreaFactory.create_batch(
            6, admin_area_type=province_area_type,
        )

    @staticmethod
    def _generate_program_with_dependencies(options):
        cash_plans_amount = options["cash_plans_amount"]
        payment_record_amount = options["payment_record_amount"]

        user = UserFactory()

        program = ProgramFactory(business_area=BusinessArea.objects.first())
        program.admin_areas.set(AdminArea.objects.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()
        rules = TargetingCriteriaRuleFactory.create_batch(
            random.randint(1, 3), targeting_criteria=targeting_criteria
        )

        for rule in rules:
            TargetingCriteriaRuleFilterFactory.create_batch(
                random.randint(1, 5), targeting_criteria_rule=rule
            )

        target_population = TargetPopulationFactory(
            created_by=user,
            candidate_list_targeting_criteria=targeting_criteria,
        )
        for _ in range(cash_plans_amount):
            cash_plan = CashPlanFactory.build(
                program=program,
                created_by=user,
                target_population=target_population,
            )

            for _ in range(payment_record_amount):
                registration_data_import = RegistrationDataImportFactory(
                    imported_by=user, business_area=BusinessArea.objects.first()
                )
                household, individuals = create_household(
                    {
                        "registration_data_import": registration_data_import,
                        "admin_area": AdminArea.objects.order_by("?").first(),
                    },
                    {"registration_data_import": registration_data_import,},
                )
                for individual in individuals:
                    DocumentFactory(individual=individual)

                household.programs.add(program)

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
        self.stdout.write(f"Generating fixtures...")
        if options["flush"]:
            call_command("flush", "--noinput")
            call_command("flush", "--noinput", database="cash_assist_datahub")
            call_command("flush", "--noinput", database="registration_datahub")
            call_command(
                "loaddata", "hct_mis_api/apps/account/fixtures/superuser.json", verbosity=0
            )
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
        if DocumentType.objects.all().count() == 0:
            if options["noinput"]:
                call_command("generatedocumenttypes")
            else:
                self.stdout.write(
                    self.style.WARNING("DocumentTypes does not exist, ")
                )

                user_input = input("Type 'y' to generate, or 'n' to cancel: ")

                if user_input.upper() == "Y" or options["noinput"]:
                    call_command("generatedocumenttypes")
                else:
                    self.stdout.write("Generation canceled")
                    return
        self._generate_admin_areas()
        for _ in range(programs_amount):
            self._generate_program_with_dependencies(options)

        # Data imports generation

        for rdi in RegistrationDataImport.objects.all()[0:40]:
            rdi_datahub = RegistrationDataImportDatahubFactory(hct_id=rdi.id)
            for _ in range(15):
                create_imported_household(
                    {"registration_data_import": rdi_datahub,},
                    {"registration_data_import": rdi_datahub,},
                )

        self.stdout.write(
            f"Generated fixtures in {(time.time() - start_time)} seconds"
        )
