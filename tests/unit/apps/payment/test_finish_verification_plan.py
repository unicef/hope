from typing import Any
from unittest import mock

from constance.test import override_config
from django.test import override_settings
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories.account import (
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
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
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hope.models import Household, Payment, PaymentVerification, PaymentVerificationPlan


@pytest.fixture
def finish_verification_setup():
    """Setup for finish verification plan tests - creates 2 records."""
    # Create minimal geo data instead of init_geo_fixtures
    country = CountryFactory()
    area_type = AreaTypeFactory(country=country, area_level=2)
    admin2_area = AreaFactory(area_type=area_type)

    business_area = create_afghanistan()
    payment_record_amount = 2
    user = UserFactory()
    role = RoleFactory(name="Releaser")
    RoleAssignmentFactory(user=user, role=role, business_area=business_area)

    program = ProgramFactory(business_area=business_area)
    program.admin_areas.set([admin2_area])

    payment_plan = PaymentPlanFactory(
        program_cycle=program.cycles.first(),
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
            imported_by=user, business_area=business_area, program=program
        )
        household, _ = create_household(
            {
                "registration_data_import": registration_data_import,
                "admin2": admin2_area,
                "program": program,
            },
            {
                "registration_data_import": registration_data_import,
                "phone_no": f"+48 609 999 {i:03d}",
            },
        )
        household.set_admin_areas()
        household.program = program
        household.refresh_from_db()

        payment = PaymentFactory(
            parent=payment_plan,
            household=household,
            head_of_household=household.head_of_household,
            delivered_quantity_usd=200,
            currency="PLN",
            status=Payment.STATUS_DISTRIBUTION_SUCCESS,
        )

        PaymentVerificationFactory(
            payment_verification_plan=payment_plan_payment_verification,
            payment=payment,
            status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        )
        EntitlementCardFactory(household=household)

    return {
        "payment_record_amount": payment_record_amount,
        "program": program,
        "verification": payment_plan.payment_verification_plans.first(),
    }


@pytest.mark.django_db
class TestFinishVerificationPlan:
    @mock.patch("hope.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(SEND_GRIEVANCES_NOTIFICATION=True, ENABLE_MAILJET=True)
    def test_create_tickets_with_admin2_same_as_in_household(
        self, mocked_requests_post: Any, finish_verification_setup
    ) -> None:
        setup = finish_verification_setup
        verification = setup["verification"]
        program = setup["program"]
        payment_record_amount = setup["payment_record_amount"]

        VerificationPlanStatusChangeServices(verification).finish()

        ticket = GrievanceTicket.objects.filter(category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION).first()
        assert ticket.programs.count() == 1
        assert ticket.programs.first().id == program.id
        household = Household.objects.get(unicef_id=ticket.household_unicef_id)
        assert ticket.admin2_id is not None
        assert household.admin2_id is not None
        assert ticket.admin2_id == household.admin2_id

        assert mocked_requests_post.call_count == payment_record_amount

    def test_finish_verification_if_pp_not_finished_yet(self, finish_verification_setup) -> None:
        setup = finish_verification_setup
        verification = setup["verification"]

        Payment.objects.all().update(status=Payment.STATUS_PENDING)
        assert not verification.payment_plan.is_reconciled
        with pytest.raises(ValidationError, match="You can finish only if reconciliation is finalized"):
            VerificationPlanStatusChangeServices(verification).finish()
