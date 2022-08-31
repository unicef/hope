import random
import time
from decimal import Decimal

from django.core.management import BaseCommand, call_command
from django.db import transaction
from django.db.models import Q

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import UserRole
from hct_mis_api.apps.cash_assist_datahub import (
    fixtures as cash_assist_datahub_fixtures,
)
from hct_mis_api.apps.cash_assist_datahub.models import Programme, Session
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceComplaintTicketWithoutExtrasFactory,
    GrievanceTicketFactory,
    SensitiveGrievanceTicketWithoutExtrasFactory,
)
from hct_mis_api.apps.household.elasticsearch_utils import rebuild_search_index
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    EntitlementCardFactory,
    create_household_for_fixtures,
)
from hct_mis_api.apps.household.models import DocumentType
from hct_mis_api.apps.payment.fixtures import (
    CashPlanPaymentVerificationFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
)
from hct_mis_api.apps.program.fixtures import CashPlanFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
    create_imported_household,
)
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetingCriteriaRuleFactory,
    TargetingCriteriaRuleFilterFactory,
    TargetPopulationFactory,
)


class Command(BaseCommand):
    help = "Generate fixtures data for project"

    def add_arguments(self, parser):
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
            help="Creates provided amount of payment records assigned to " "household and cash plan.",
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
    def _generate_program_with_dependencies(options, business_area_index):
        cash_plans_amount = options["cash_plans_amount"]
        payment_record_amount = options["payment_record_amount"]

        user = UserFactory()
        business_area = BusinessArea.objects.all()[business_area_index]

        program = ProgramFactory(business_area=business_area)
        targeting_criteria = TargetingCriteriaFactory()
        rules = TargetingCriteriaRuleFactory.create_batch(random.randint(1, 3), targeting_criteria=targeting_criteria)

        for rule in rules:
            TargetingCriteriaRuleFilterFactory.create_batch(random.randint(1, 5), targeting_criteria_rule=rule)

        target_population = TargetPopulationFactory(
            created_by=user,
            targeting_criteria=targeting_criteria,
            business_area=business_area,
        )
        for _ in range(cash_plans_amount):
            cash_plan = CashPlanFactory(
                program=program,
                business_area=business_area,
            )
            cash_plan.save()
            for _ in range(payment_record_amount):
                registration_data_import = RegistrationDataImportFactory(imported_by=user, business_area=business_area)
                household, individuals = create_household_for_fixtures(
                    {
                        "registration_data_import": registration_data_import,
                        "business_area": business_area,
                        "admin_area": Area.objects.filter(area_type__business_area=business_area).order_by("?").first(),
                    },
                    {"registration_data_import": registration_data_import},
                )
                for individual in individuals:
                    DocumentFactory(individual=individual)

                household.programs.add(program)
                if household.admin_area:
                    program.admin_areas.add(household.admin_area)

                payment_record = PaymentRecordFactory(
                    cash_plan=cash_plan,
                    household=household,
                    target_population=target_population,
                    delivered_quantity_usd=None,
                    business_area=business_area,
                )
                payment_record.delivered_quantity_usd = Decimal(
                    cash_plan.exchange_rate * payment_record.delivered_quantity
                ).quantize(Decimal(".01"))
                payment_record.save()

                should_create_grievance = random.choice((True, False))
                if should_create_grievance:
                    grievance_type = random.choice(("feedback", "sensitive", "complaint"))
                    should_contain_payment_record = random.choice((True, False))
                    switch_dict = {
                        "feedback": lambda: GrievanceTicketFactory(
                            admin2=Area.objects.filter(area_type__business_area=business_area, area_type__area_level=2)
                            .order_by("?")
                            .first()
                            .name,
                        ),
                        "sensitive": lambda: SensitiveGrievanceTicketWithoutExtrasFactory(
                            household=household,
                            individual=random.choice(individuals),
                            payment_record=payment_record if should_contain_payment_record else None,
                        ),
                        "complaint": lambda: GrievanceComplaintTicketWithoutExtrasFactory(
                            household=household,
                            individual=random.choice(individuals),
                            payment_record=payment_record if should_contain_payment_record else None,
                        ),
                    }

                    grievance_ticket = switch_dict.get(grievance_type)()

                EntitlementCardFactory(household=household)
        CashPlanPaymentVerificationFactory.create_batch(1)
        PaymentVerificationFactory.create_batch(10)

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Generating fixtures...")
        if options["flush"]:
            call_command("flush", "--noinput")
            call_command("flush", "--noinput", database="cash_assist_datahub_mis")
            call_command("flush", "--noinput", database="cash_assist_datahub_ca")
            call_command("flush", "--noinput", database="cash_assist_datahub_erp")
            call_command("flush", "--noinput", database="registration_datahub")
            call_command(
                "loaddata",
                "hct_mis_api/apps/account/fixtures/superuser.json",
                verbosity=0,
            )
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
        if not UserRole.objects.count():
            call_command("generateroles")
        for index in range(business_area_amount):
            for _ in range(programs_amount):
                self._generate_program_with_dependencies(options, index)

        # Data imports generation

        for rdi in RegistrationDataImport.objects.all():
            rdi_datahub = RegistrationDataImportDatahubFactory(
                name=rdi.name, hct_id=rdi.id, business_area_slug=rdi.business_area.slug
            )
            rdi.datahub_id = rdi_datahub.id
            rdi.save()
            for _ in range(10):
                create_imported_household(
                    {"registration_data_import": rdi_datahub},
                    {"registration_data_import": rdi_datahub},
                )
        session = Session(source=Session.SOURCE_CA, status=Session.STATUS_READY)
        session.save()
        cash_assist_datahub_fixtures.ServiceProviderFactory.create_batch(10, session=session)
        cash_assist_datahub_fixtures.CashPlanFactory.create_batch(10, session=session)
        cash_assist_datahub_fixtures.PaymentRecordFactory.create_batch(10, session=session)

        for _ in range(programs_amount):
            used_ids = list(Programme.objects.values_list("mis_id", flat=True))
            mis_id = Program.objects.filter(~Q(id__in=used_ids)).first().id
            programme = cash_assist_datahub_fixtures.ProgrammeFactory(session=session, mis_id=mis_id)
            programme.save()

        if not options["noreindex"]:
            rebuild_search_index()

        self.stdout.write(f"Generated fixtures in {(time.time() - start_time)} seconds")
