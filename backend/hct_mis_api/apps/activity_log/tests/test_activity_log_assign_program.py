from django.core.management import call_command
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory


class TestLogsAssignProgram(TestCase):
    multi_db = True

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory(first_name="User", last_name="WithLastName")
        cls.program = ProgramFactory(business_area=cls.business_area)

    def test_assign_program_to_existing_logs(self) -> None:
        program_cycle = ProgramCycleFactory(program=self.program, iteration=2)

        rdi = RegistrationDataImportFactory(business_area=self.business_area, program_id=self.program.pk)
        tp = TargetPopulationFactory(program=self.program, business_area=self.business_area)
        payment_plan = PaymentPlanFactory(
            business_area=self.business_area, program=self.program, program_cycle=program_cycle
        )
        payment = PaymentFactory(parent=payment_plan, business_area=self.business_area)
        cash_plan = CashPlanFactory(business_area=self.business_area, program=self.program)
        PaymentVerificationSummaryFactory(generic_fk_obj=payment_plan)
        payment_verification_plan = PaymentVerificationPlanFactory(generic_fk_obj=payment_plan)
        payment_verification = PaymentVerificationFactory(
            payment_verification_plan=payment_verification_plan, generic_fk_obj=payment
        )
        grievance_ticket = GrievanceTicketFactory(business_area=self.business_area)
        grievance_ticket.programs.add(self.program)
        # TODO: update after changes for Ind and HH collections/representations
        # individual = IndividualFactory(household=None, program=cls.program)
        # household = HouseholdFactory(head_of_household=individual, program=cls.program)

        # log for Program
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=self.program,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(self.program),
            changes=dict(),
        )
        # log for RegistrationDataImport
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=rdi,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(rdi),
            changes=dict(),
        )
        # log for TargetPopulation
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=tp,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(tp),
            changes=dict(),
        )
        # log for PaymentPlan
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=payment_plan,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(payment_plan),
            changes=dict(),
        )
        # log for CashPlan
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=cash_plan,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(cash_plan),
            changes=dict(),
        )
        # log for PaymentVerificationPlan
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=payment_verification_plan,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(payment_verification_plan),
            changes=dict(),
        )
        # log for PaymentVerification
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=payment_verification,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(payment_verification),
            changes=dict(),
        )
        # log for GrievanceTicket
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=grievance_ticket,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(grievance_ticket),
            changes=dict(),
        )
        # TODO: update after changes for Ind and HH collections/representations
        # # log for Individual
        # LogEntry.objects.create(
        #     action=LogEntry.CREATE,
        #     content_object=individual,
        #     user=cls.user,
        #     business_area=cls.business_area,
        #     object_repr=str(individual),
        #     changes=dict(),
        # )
        # # log for Household
        # LogEntry.objects.create(
        #     action=LogEntry.CREATE,
        #     content_object=household,
        #     user=cls.user,
        #     business_area=cls.business_area,
        #     object_repr=str(household),
        #     changes=dict(),
        # )

        self.assertEqual(LogEntry.objects.filter(programs__isnull=True).count(), 8)

        call_command("activity_log_assign_program")

        self.assertEqual(LogEntry.objects.filter(programs__isnull=True).count(), 0)
        self.assertEqual(LogEntry.objects.filter(programs__pk=self.program.pk).count(), 8)

    def test_raise_value_error_with_wrong_model(self) -> None:
        rdi = RegistrationDataImportFactory(business_area=self.business_area, program=self.program)
        rdi_log = LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=rdi,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(rdi),
            changes=dict(),
        )
        # don't have program_id field in User model
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=self.user,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(self.user),
            changes=dict(),
        )

        self.assertEqual(LogEntry.objects.filter(programs__isnull=True).count(), 2)

        with self.assertRaisesMessage(ValueError, "Can not found 'class_name' and 'nested_field' for class User"):
            call_command("activity_log_assign_program")

        # check transaction.atomic
        rdi_log.refresh_from_db()
        self.assertIsNone(rdi_log.programs)

        self.assertEqual(LogEntry.objects.filter(programs__isnull=True).count(), 2)
