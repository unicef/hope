from typing import Any
from unittest import mock

from constance.test import override_config
from django.core.management import call_command
from django.test import TestCase, override_settings

from extras.test_utils.factories.account import (
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    EntitlementCardFactory,
    create_household,
)
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.geo.models import Area
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.models import Household
from hope.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hope.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)


class TestFinishVerificationPlan(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init_geo_fixtures")
        business_area = create_afghanistan()
        payment_record_amount = 10
        user = UserFactory()
        role = RoleFactory(name="Releaser")
        RoleAssignmentFactory(user=user, role=role, business_area=business_area)

        afghanistan_areas_qs = Area.objects.filter(area_type__area_level=2, area_type__country__iso_code3="AFG")

        cls.program = ProgramFactory(business_area=business_area)
        cls.program.admin_areas.set(afghanistan_areas_qs.order_by("?")[:3])

        payment_plan = PaymentPlanFactory(
            program_cycle=cls.program.cycles.first(),
            business_area=business_area,
            created_by=user,
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        payment_plan_payment_verification = PaymentVerificationPlanFactory(
            status=PaymentVerificationPlan.STATUS_PENDING,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
            payment_plan=payment_plan,
        )
        for i in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=user, business_area=business_area, program=cls.program
            )
            household, _ = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin2": afghanistan_areas_qs.order_by("?").first(),
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

            payment = PaymentFactory(
                parent=payment_plan,
                household=household,
                head_of_household=household.head_of_household,
                delivered_quantity_usd=200,
                currency="PLN",
            )

            PaymentVerificationFactory(
                payment_verification_plan=payment_plan_payment_verification,
                payment=payment,
                status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
            )
            EntitlementCardFactory(household=household)
        cls.verification = payment_plan.payment_verification_plans.first()

    @mock.patch("hope.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(SEND_GRIEVANCES_NOTIFICATION=True, ENABLE_MAILJET=True)
    def test_create_tickets_with_admin2_same_as_in_household(self, mocked_requests_post: Any) -> None:
        VerificationPlanStatusChangeServices(self.verification).finish()

        ticket = GrievanceTicket.objects.filter(category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION).first()
        assert ticket.programs.count() == 1
        assert ticket.programs.first().id == self.program.id
        household = Household.objects.get(unicef_id=ticket.household_unicef_id)
        assert ticket.admin2_id is not None
        assert household.admin2_id is not None
        assert ticket.admin2_id == household.admin2_id

        assert mocked_requests_post.call_count == 10
