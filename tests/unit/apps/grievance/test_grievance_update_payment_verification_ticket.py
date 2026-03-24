"""Tests for grievance update payment verification ticket functionality."""

from typing import Any, Callable

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.factories.grievance import (
    TicketPaymentVerificationDetailsFactory,
)
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, PaymentVerification, PaymentVerificationPlan, Program


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(
        slug="afghanistan",
        name="Afghanistan",
    )


@pytest.fixture
def partner() -> PartnerFactory:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: PartnerFactory) -> UserFactory:
    return UserFactory(partner=partner, first_name="TestUser")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    program = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )
    ProgramCycleFactory(program=program)
    return program


@pytest.fixture
def household(afghanistan: BusinessArea, program: Program) -> HouseholdFactory:
    individual = IndividualFactory(
        full_name="Jenna Franklin",
        given_name="Jenna",
        family_name="Franklin",
        phone_no="001-296-358-5428-607",
        birth_date="1969-11-29",
        business_area=afghanistan,
        program=program,
        household=None,
    )
    household = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        head_of_household=individual,
    )
    individual.household = household
    individual.save()

    return household


@pytest.fixture
def payment_verification_ticket(afghanistan: BusinessArea, program: Program, household: HouseholdFactory):
    payment_plan = PaymentPlanFactory(
        name="TEST",
        program_cycle=program.cycles.first(),
        business_area=afghanistan,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    payment_verification_plan = PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        status=PaymentVerificationPlan.STATUS_ACTIVE,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        household=household,
        currency="PLN",
        program=program,
        collector=household.head_of_household,
    )
    payment_verification = PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan,
        payment=payment,
        status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
    )
    ticket = TicketPaymentVerificationDetailsFactory(
        payment_verification=payment_verification,
        ticket__status=GrievanceTicket.STATUS_IN_PROGRESS,
        ticket__business_area=afghanistan,
    )
    ticket.ticket.programs.set([program])

    return ticket


@pytest.fixture
def detail_url(afghanistan: BusinessArea, payment_verification_ticket) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(payment_verification_ticket.ticket.pk),
        },
    )


def test_update_payment_verification_ticket_with_new_received_amount_extras(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    payment_verification_ticket,
    detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program)

    client = api_client(user)
    data = {
        "extras": {
            "ticket_payment_verification_details_extras": {
                "new_received_amount": 1234.99,
                "new_status": PaymentVerification.STATUS_RECEIVED,
            }
        }
    }

    response = client.patch(detail_url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["ticket_details"]["new_status"] == PaymentVerification.STATUS_RECEIVED
    assert response.json()["ticket_details"]["new_received_amount"] == "1234.99"


def test_payment_verification_ticket_approve_payment_details(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    payment_verification_ticket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION],
        afghanistan,
        program,
    )

    # Update status for approval
    payment_verification_ticket.ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
    payment_verification_ticket.ticket.save()

    client = api_client(user)
    input_data = {
        "version": payment_verification_ticket.ticket.version,
        "approve_status": True,
    }

    assert payment_verification_ticket.approve_status is False

    response = client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-approve-payment-details",
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(payment_verification_ticket.ticket.pk),
            },
        ),
        input_data,
        format="json",
    )

    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in resp_data

    payment_verification_ticket.refresh_from_db()
    assert payment_verification_ticket.approve_status is True
