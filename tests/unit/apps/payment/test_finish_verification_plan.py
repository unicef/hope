from typing import Any
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings

from constance.test import override_config

from hct_mis_api.apps.account.fixtures import RoleFactory, UserFactory, UserRoleFactory
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
        super().setUpTestData()
        business_area = create_afghanistan()
        payment_record_amount = 10
        user = UserFactory()
        role = RoleFactory(name="Releaser")
        UserRoleFactory(user=user, role=role, business_area=business_area)

        afghanistan_areas_qs = Area.objects.filter(area_type__area_level=2, area_type__country__iso_code3="AFG")

        cls.program = ProgramFactory(business_area=business_area)
        cls.program.admin_areas.set(afghanistan_areas_qs.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()

        target_population = TargetPopulationFactory(
            created_by=user,
            targeting_criteria=targeting_criteria,
            business_area=business_area,
            program=cls.program,
        )
        cash_plan = CashPlanFactory(
            program=cls.program,
            business_area=business_area,
        )
        cash_plan.save()
        cash_plan_payment_verification = PaymentVerificationPlanFactory(
            status=PaymentVerificationPlan.STATUS_PENDING,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
            payment_plan_obj=cash_plan,
        )
        for i in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=user, business_area=business_area, program=cls.program
            )
            household, _ = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": afghanistan_areas_qs.order_by("?").first(),
                    "program": cls.program,
                },
                {
                    "registration_data_import": registration_data_import,
                    "phone_no": f"+48 609 999 {i:03d}",
                },
            )
            household.set_admin_areas()
            household.program = cls.program
            household.refresh_from_db()

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
                payment_obj=payment_record,
                status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
            )
            EntitlementCardFactory(household=household)
        cls.verification = cash_plan.get_payment_verification_plans.first()

    @mock.patch("hct_mis_api.apps.utils.mailjet.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(SEND_GRIEVANCES_NOTIFICATION=True, ENABLE_MAILJET=True)
    def test_create_tickets_with_admin2_same_as_in_household(self, mocked_requests_post: Any) -> None:
        VerificationPlanStatusChangeServices(self.verification).finish()

        ticket = GrievanceTicket.objects.filter(category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION).first()
        self.assertEqual(ticket.programs.count(), 1)
        self.assertEqual(ticket.programs.first().id, self.program.id)
        household = Household.objects.get(unicef_id=ticket.household_unicef_id)
        self.assertIsNotNone(ticket.admin2_id)
        self.assertIsNotNone(household.admin2_id)
        self.assertEqual(ticket.admin2_id, household.admin2_id)

        self.assertEqual(mocked_requests_post.call_count, 10)
