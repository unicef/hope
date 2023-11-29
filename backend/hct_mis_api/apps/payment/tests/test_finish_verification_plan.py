from django.conf import settings
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import EntitlementCardFactory, create_household
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hct_mis_api.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)


class TestFinishVerificationPlan(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        business_area = create_afghanistan()
        payment_record_amount = 10
        user = UserFactory()

        ###

        program = ProgramFactory(business_area=business_area)
        program.admin_areas.set(Area.objects.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()

        target_population = TargetPopulationFactory(
            created_by=user,
            targeting_criteria=targeting_criteria,
            business_area=business_area,
        )
        cash_plan = CashPlanFactory(
            program=program,
            business_area=business_area,
        )
        cash_plan.save()
        cash_plan_payment_verification = PaymentVerificationPlanFactory(
            status=PaymentVerificationPlan.STATUS_PENDING,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
            generic_fk_obj=cash_plan,
        )
        for i in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(imported_by=user, business_area=business_area)
            household, _ = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": Area.objects.order_by("?").first(),
                },
                {
                    "registration_data_import": registration_data_import,
                    "phone_no": f"+48 609 999 {i:03d}",
                },
            )
            household.set_admin_areas()
            household.programs.add(program)

            payment_record = PaymentRecordFactory(
                parent=cash_plan,
                household=household,
                head_of_household=household.head_of_household,
                target_population=target_population,
                delivered_quantity_usd=200,
                currency="PLN",
            )

            PaymentVerificationFactory(
                payment_verification_plan=cash_plan_payment_verification,
                generic_fk_obj=payment_record,
                status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
            )
            EntitlementCardFactory(household=household)
        cls.verification = cash_plan.get_payment_verification_plans.first()

    def test_create_tickets_with_admin2_same_as_in_household(self) -> None:
        VerificationPlanStatusChangeServices(self.verification).finish()

        ticket = GrievanceTicket.objects.filter(category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION).first()
        household = Household.objects.get(unicef_id=ticket.household_unicef_id)
        self.assertIsNotNone(household.admin2_id)
        self.assertIsNotNone(ticket.admin2_id)
        self.assertEqual(ticket.admin2_id, household.admin2_id)
