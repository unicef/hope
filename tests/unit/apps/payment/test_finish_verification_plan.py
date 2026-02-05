from unittest import mock

from constance.test import override_config
from django.test import override_settings
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import EntitlementCardFactory, HouseholdFactory
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.grievance.models import GrievanceTicket, TicketPaymentVerificationDetails
from hope.apps.payment.services.verification_plan_status_change_services import VerificationPlanStatusChangeServices
from hope.models import Household, Payment, PaymentVerification, PaymentVerificationPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def country():
    return CountryFactory()


@pytest.fixture
def admin2_area(country):
    area_type = AreaTypeFactory(country=country, area_level=2)
    return AreaFactory(area_type=area_type)


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def role_assignment(user, business_area):
    role = RoleFactory(name="Releaser")
    return RoleAssignmentFactory(user=user, role=role, business_area=business_area)


@pytest.fixture
def program(business_area, admin2_area):
    program = ProgramFactory(business_area=business_area)
    program.admin_areas.add(admin2_area)
    return program


@pytest.fixture
def program_cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def payment_plan(program_cycle, business_area, user):
    return PaymentPlanFactory(
        program_cycle=program_cycle,
        business_area=business_area,
        created_by=user,
    )


@pytest.fixture
def payment_verification_plan(payment_plan):
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    return PaymentVerificationPlanFactory(
        status=PaymentVerificationPlan.STATUS_PENDING,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
        payment_plan=payment_plan,
    )


@pytest.fixture
def household(business_area, program, admin2_area, user):
    registration_data_import = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        imported_by=user,
    )
    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        admin2=admin2_area,
    )
    household.set_admin_areas()
    return household


@pytest.fixture
def payment_verification_records(payment_verification_plan, household):
    households = [household, HouseholdFactory(program=household.program, business_area=household.business_area)]
    records = []
    for record_household in households:
        if record_household.admin2_id is None:
            record_household.admin2 = household.admin2
            record_household.set_admin_areas()
        payment = PaymentFactory(
            parent=payment_verification_plan.payment_plan,
            household=record_household,
            head_of_household=record_household.head_of_household,
            collector=record_household.head_of_household,
            delivered_quantity_usd=200,
            currency="PLN",
            status=Payment.STATUS_DISTRIBUTION_SUCCESS,
        )
        verification = PaymentVerificationFactory(
            payment_verification_plan=payment_verification_plan,
            payment=payment,
            status=PaymentVerification.STATUS_PENDING,
        )
        EntitlementCardFactory(household=record_household)
        records.append({"household": record_household, "payment": payment, "verification": verification})
    return records


@mock.patch("hope.apps.utils.celery_tasks.requests.post")
@override_settings(EMAIL_SUBJECT_PREFIX="test")
@override_config(SEND_GRIEVANCES_NOTIFICATION=True, ENABLE_MAILJET=True)
def test_create_tickets_with_admin2_same_as_in_household(
    mocked_requests_post,
    payment_verification_plan,
    program,
    payment_verification_records,
    role_assignment,
):
    for record in payment_verification_records:
        verification = record["verification"]
        verification.status = PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
        verification.save(update_fields=["status"])

    VerificationPlanStatusChangeServices(payment_verification_plan).finish()

    tickets = GrievanceTicket.objects.filter(category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION)
    assert tickets.count() == len(payment_verification_records)
    ticket = tickets.first()
    assert ticket.programs.count() == 1
    assert ticket.programs.first().id == program.id
    household = Household.objects.get(unicef_id=ticket.household_unicef_id)
    assert ticket.admin2_id is not None
    assert household.admin2_id is not None
    assert ticket.admin2_id == household.admin2_id

    assert mocked_requests_post.call_count == len(payment_verification_records)


def test_finish_verification_if_pp_not_finished_yet(payment_verification_plan, payment_verification_records):
    Payment.objects.all().update(status=Payment.STATUS_PENDING)
    assert not payment_verification_plan.payment_plan.is_reconciled
    with pytest.raises(ValidationError, match="You can finish only if reconciliation is finalized"):
        VerificationPlanStatusChangeServices(payment_verification_plan).finish()


@override_config(SEND_GRIEVANCES_NOTIFICATION=False, ENABLE_MAILJET=False)
def test_create_tickets_for_not_received_status(payment_verification_plan, payment_verification_records):
    verification = payment_verification_records[0]["verification"]
    verification.status = PaymentVerification.STATUS_NOT_RECEIVED
    verification.save(update_fields=["status"])

    VerificationPlanStatusChangeServices(payment_verification_plan).finish()

    assert TicketPaymentVerificationDetails.objects.filter(
        payment_verification_status=PaymentVerification.STATUS_NOT_RECEIVED
    ).exists()


@override_config(SEND_GRIEVANCES_NOTIFICATION=False, ENABLE_MAILJET=False)
def test_create_grievance_ticket_returns_when_no_verifications(payment_verification_plan, payment_verification_records):
    for record in payment_verification_records:
        verification = record["verification"]
        verification.status = PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
        verification.save(update_fields=["status"])

    service = VerificationPlanStatusChangeServices(payment_verification_plan)
    initial_count = GrievanceTicket.objects.count()

    service._create_grievance_ticket_for_status(payment_verification_plan, PaymentVerification.STATUS_NOT_RECEIVED)

    assert GrievanceTicket.objects.count() == initial_count


@override_config(SEND_GRIEVANCES_NOTIFICATION=False, ENABLE_MAILJET=False)
def test_finish_verification_deletes_pending_verifications(payment_verification_plan, payment_verification_records):
    pending_verification = payment_verification_records[0]["verification"]

    VerificationPlanStatusChangeServices(payment_verification_plan).finish()

    assert not PaymentVerification.objects.filter(id=pending_verification.id).exists()
