import random
import time
from argparse import ArgumentParser
from decimal import Decimal
from functools import partial
from typing import TYPE_CHECKING, Any, Callable

from django.core.management import BaseCommand, call_command
from django.db import transaction
from extras.test_utils.factories.account import UserFactory, create_superuser
from extras.test_utils.factories.grievance import (
    GrievanceComplaintTicketWithoutExtrasFactory,
    GrievanceTicketFactory,
    SensitiveGrievanceTicketWithoutExtrasFactory,
)
from extras.test_utils.factories.household import (
    DocumentFactory,
    EntitlementCardFactory,
    create_household_for_fixtures,
)
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from extras.test_utils.factories.targeting import (
    TargetingCriteriaRuleFactory,
    TargetingCriteriaRuleFilterFactory,
)

from hope.apps.account.models import RoleAssignment
from hope.apps.core.models import BusinessArea
from hope.apps.geo.models import Area
from hope.apps.household.models import DocumentType
from hope.apps.utils.elasticsearch_utils import rebuild_search_index

if TYPE_CHECKING:
    from hope.apps.grievance.models import GrievanceTicket


class Command(BaseCommand):
    help = "Generate fixtures data for project"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--program",
            dest="programs_amount",
            const=3,
            default=3,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of program objects.",
        )

        parser.add_argument(
            "--cash-plan",
            dest="cash_plans_amount",
            const=3,
            default=3,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of cash plans for one program.",
        )

        parser.add_argument(
            "--payment-record",
            dest="payment_record_amount",
            const=3,
            default=3,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of payment records assigned to household and cash plan.",
        )
        parser.add_argument(
            "--business-area",
            dest="business_area_amount",
            const=1,
            default=1,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of business areas with data.",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Suppresses all user prompts.",
        )
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Suppresses all user prompts.",
        )
        parser.add_argument(
            "--noreindex",
            action="store_true",
            help="Suppresses Elasticsearch reindex.",
        )

    @staticmethod
    def _generate_program_with_dependencies(options: dict, business_area_index: int) -> None:
        cash_plans_amount = options["cash_plans_amount"]
        payment_record_amount = options["payment_record_amount"]

        user = UserFactory()
        business_area = BusinessArea.objects.all()[business_area_index]

        program = ProgramFactory(business_area=business_area)

        for _ in range(cash_plans_amount):
            payment_plan = PaymentPlanFactory(
                program=program,
                business_area=business_area,
            )
            rules = TargetingCriteriaRuleFactory.create_batch(random.randint(1, 3), payment_plan=payment_plan)

            for rule in rules:
                TargetingCriteriaRuleFilterFactory.create_batch(random.randint(1, 5), targeting_criteria_rule=rule)
            for _ in range(payment_record_amount):
                registration_data_import = RegistrationDataImportFactory(imported_by=user, business_area=business_area)
                household, individuals = create_household_for_fixtures(
                    {
                        "registration_data_import": registration_data_import,
                        "business_area": business_area,
                        "admin1": Area.objects.filter(area_type__business_area=business_area).order_by("?").first(),
                        "program": program,
                    },
                    {"registration_data_import": registration_data_import},
                )
                for individual in individuals:
                    DocumentFactory(individual=individual)

                if household.admin1:
                    program.admin_areas.add(household.admin1)

                payment = PaymentFactory(
                    parent=payment_plan,
                    household=household,
                    delivered_quantity_usd=None,
                    business_area=business_area,
                )
                payment.delivered_quantity_usd = Decimal(
                    payment_plan.exchange_rate * payment.delivered_quantity
                ).quantize(Decimal(".01"))
                payment.save()

                should_create_grievance = random.choice((True, False))
                if should_create_grievance:
                    grievance_type = random.choice(("feedback", "sensitive", "complaint"))
                    should_contain_payment_record = random.choice((True, False))
                    switch_dict: dict[str, Callable[[], GrievanceTicket]] = {
                        "feedback": partial(
                            GrievanceTicketFactory,
                            admin2=Area.objects.filter(
                                area_type__business_area=business_area,
                                area_type__area_level=2,
                            )
                            .order_by("?")
                            .first()
                            .name,
                        ),
                        "sensitive": partial(
                            SensitiveGrievanceTicketWithoutExtrasFactory,
                            household=household,
                            individual=random.choice(individuals),
                            payment=payment if should_contain_payment_record else None,
                        ),
                        "complaint": partial(
                            GrievanceComplaintTicketWithoutExtrasFactory,
                            household=household,
                            individual=random.choice(individuals),
                            payment=payment if should_contain_payment_record else None,
                        ),
                    }

                    switch_dict[grievance_type]()

                EntitlementCardFactory(household=household)
        PaymentVerificationPlanFactory()
        PaymentVerificationFactory.create_batch(10)

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Generating fixtures...")
        if options["flush"]:
            call_command("flush", "--noinput")
            create_superuser()

        start_time = time.time()
        programs_amount = options["programs_amount"]
        business_area_amount = options["business_area_amount"]
        business_areas = BusinessArea.objects.all().count()
        if not business_areas:
            if options["noinput"]:
                call_command("loadbusinessareas")
            else:
                self.stdout.write(self.style.WARNING("BusinessAreas does not exist, "))

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
                self.stdout.write(self.style.WARNING("DocumentTypes does not exist, "))

                user_input = input("Type 'y' to generate, or 'n' to cancel: ")

                if user_input.upper() == "Y" or options["noinput"]:
                    call_command("generatedocumenttypes")
                else:
                    self.stdout.write("Generation canceled")
                    return
        if not RoleAssignment.objects.count():
            call_command("generateroles")
        for index in range(business_area_amount):
            for _ in range(programs_amount):
                self._generate_program_with_dependencies(options, index)

        if not options["noreindex"]:
            rebuild_search_index()

        self.stdout.write(f"Generated fixtures in {(time.time() - start_time)} seconds")
