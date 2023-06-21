from django.core.management import call_command

from apps.grievance.models import GrievanceTicket
from apps.payment.models import (
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
)

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.activity_log.utils import create_diff
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation


class TestLogsAssignProgram(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")
        user = UserFactory(first_name="User", last_name="WithLastName")

        cls.program = ProgramFactory(business_area=business_area)

        rdi = RegistrationDataImportFactory(business_area=business_area, program_id=cls.program.pk)
        tp = TargetPopulationFactory(program=cls.program, business_area=business_area)
        payment_plan = PaymentPlanFactory(
            business_area=business_area, program=cls.program, program_cycle=ProgramCycleFactory(program=cls.program)
        )
        cash_plan = CashPlanFactory(business_area=business_area, program=cls.program)
        payment_verification_plan = PaymentVerificationPlanFactory(payment_plan_obj=payment_plan)
        payment_verification = PaymentVerificationFactory(payment_verification_plan=payment_verification_plan)
        grievance_ticket = GrievanceTicketFactory(business_area=business_area, programme=cls.program)
        # TODO: update after changes for Ind and HH collections/representations
        # individual = IndividualFactory(household=None, program=cls.program)
        # household = HouseholdFactory(head_of_household=individual, program=cls.program)

        # log for Program
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=cls.program,
            user=user,
            program=None,
            business_area=business_area,
            object_repr=str(cls.program),
            changes=create_diff(None, cls.program, Program.ACTIVITY_LOG_MAPPING),
        )
        # log for RegistrationDataImport
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=rdi,
            user=user,
            program=None,
            business_area=business_area,
            object_repr=str(rdi),
            changes=create_diff(None, rdi, RegistrationDataImport.ACTIVITY_LOG_MAPPING),
        )
        # log for TargetPopulation
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=tp,
            user=user,
            program=None,
            business_area=business_area,
            object_repr=str(tp),
            changes=create_diff(None, tp, TargetPopulation.ACTIVITY_LOG_MAPPING),
        )
        # log for PaymentPlan
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=payment_plan,
            user=user,
            program=None,
            business_area=business_area,
            object_repr=str(payment_plan),
            changes=create_diff(None, payment_plan, PaymentPlan.ACTIVITY_LOG_MAPPING),
        )
        # log for CashPlan
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=cash_plan,
            user=user,
            program=None,
            business_area=business_area,
            object_repr=str(cash_plan),
            changes=create_diff(None, cash_plan, PaymentPlan.ACTIVITY_LOG_MAPPING),
        )
        # log for PaymentVerificationPlan
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=payment_verification_plan,
            user=user,
            program=None,
            business_area=business_area,
            object_repr=str(payment_verification_plan),
            changes=create_diff(None, payment_verification_plan, PaymentVerificationPlan.ACTIVITY_LOG_MAPPING),
        )
        # log for PaymentVerification
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=payment_verification,
            user=user,
            program=None,
            business_area=business_area,
            object_repr=str(payment_verification),
            changes=create_diff(None, payment_verification, PaymentVerification.ACTIVITY_LOG_MAPPING),
        )
        # log for GrievanceTicket
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=grievance_ticket,
            user=user,
            program=None,
            business_area=business_area,
            object_repr=str(grievance_ticket),
            changes=create_diff(None, grievance_ticket, GrievanceTicket.ACTIVITY_LOG_MAPPING),
        )
        # TODO: update after changes for Ind and HH collections/representations
        # # log for Individual
        # LogEntry.objects.create(
        #     action=LogEntry.CREATE,
        #     content_object=individual,
        #     user=user,
        #     program=None,
        #     business_area=business_area,
        #     object_repr=str(individual),
        #     changes=create_diff(None, individual, Individual.ACTIVITY_LOG_MAPPING),
        # )
        # # log for Household
        # LogEntry.objects.create(
        #     action=LogEntry.CREATE,
        #     content_object=household,
        #     user=user,
        #     program=None,
        #     business_area=business_area,
        #     object_repr=str(household),
        #     changes=create_diff(None, household, Household.ACTIVITY_LOG_MAPPING),
        # )

    def test_assign_program_to_existing_logs(self) -> None:
        assert LogEntry.objects.filter(program__isnull=True).count() == 8

        call_command("activity_log_assign_program")

        assert LogEntry.objects.filter(program__isnull=True).count() == 0
        assert LogEntry.objects.filter(program_id=self.program.pk).count() == 8
