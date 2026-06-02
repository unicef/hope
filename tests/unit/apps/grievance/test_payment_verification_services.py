from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
from extras.test_utils.factories.grievance import TicketPaymentVerificationDetailsFactory
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from hope.apps.grievance.models import GrievanceTicket, TicketPaymentVerificationDetails
from hope.apps.grievance.services.payment_verification_services import (
    update_payment_verification_service,
    update_ticket_payment_verification_service,
)
from hope.models import BusinessArea, PaymentVerification, PaymentVerificationPlan, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def payment_verification(business_area: BusinessArea, program: Program) -> PaymentVerification:
    payment_plan = PaymentPlanFactory(
        program_cycle=program.cycles.first(),
        business_area=business_area,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    verification_plan = PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        status=PaymentVerificationPlan.STATUS_ACTIVE,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        program=program,
        delivered_quantity=Decimal("100.00"),
    )
    return PaymentVerificationFactory(
        payment_verification_plan=verification_plan,
        payment=payment,
        status=PaymentVerification.STATUS_PENDING,
    )


@pytest.fixture
def details(
    business_area: BusinessArea, payment_verification: PaymentVerification
) -> TicketPaymentVerificationDetails:
    return TicketPaymentVerificationDetailsFactory(
        ticket__status=GrievanceTicket.STATUS_IN_PROGRESS,
        ticket__business_area=business_area,
        payment_verification=payment_verification,
        approve_status=True,
    )


def test_update_payment_verification_returns_early_when_not_approved(
    details: TicketPaymentVerificationDetails, payment_verification: PaymentVerification
) -> None:
    details.approve_status = False
    details.save()

    result = update_payment_verification_service(details.ticket, None)

    payment_verification.refresh_from_db()
    assert result == [details.ticket]
    assert payment_verification.status == PaymentVerification.STATUS_PENDING


def test_update_payment_verification_sets_not_received_status(
    details: TicketPaymentVerificationDetails, payment_verification: PaymentVerification
) -> None:
    details.new_status = PaymentVerification.STATUS_NOT_RECEIVED
    details.save()

    update_payment_verification_service(details.ticket, None)

    payment_verification.refresh_from_db()
    assert payment_verification.status == PaymentVerification.STATUS_NOT_RECEIVED


def test_update_payment_verification_sets_received_when_amount_matches_delivered(
    details: TicketPaymentVerificationDetails, payment_verification: PaymentVerification
) -> None:
    details.new_received_amount = Decimal("100.00")
    details.save()

    update_payment_verification_service(details.ticket, None)

    payment_verification.refresh_from_db()
    assert payment_verification.status == PaymentVerification.STATUS_RECEIVED
    assert payment_verification.received_amount == Decimal("100.00")


def test_update_payment_verification_sets_received_with_issues_when_amount_differs(
    details: TicketPaymentVerificationDetails, payment_verification: PaymentVerification
) -> None:
    details.new_received_amount = Decimal("50.00")
    details.save()

    update_payment_verification_service(details.ticket, None)

    payment_verification.refresh_from_db()
    assert payment_verification.status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES


def test_update_ticket_raises_when_ticket_not_in_progress(details: TicketPaymentVerificationDetails) -> None:
    details.ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
    details.ticket.save()

    with pytest.raises(ValidationError):
        update_ticket_payment_verification_service(details.ticket, {}, {})


def test_update_ticket_updates_details_when_single_verification(details: TicketPaymentVerificationDetails) -> None:
    extras = {
        "ticket_payment_verification_details_extras": {
            "new_received_amount": Decimal("75.00"),
            "new_status": PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        }
    }

    update_ticket_payment_verification_service(details.ticket, extras, {})

    details.refresh_from_db()
    assert details.new_received_amount == Decimal("75.00")
    assert details.new_status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES


def test_update_ticket_skips_update_with_multiple_verifications(
    details: TicketPaymentVerificationDetails, payment_verification: PaymentVerification
) -> None:
    details.payment_verifications.add(payment_verification)
    extras = {
        "ticket_payment_verification_details_extras": {
            "new_received_amount": Decimal("75.00"),
            "new_status": PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        }
    }

    update_ticket_payment_verification_service(details.ticket, extras, {})

    details.refresh_from_db()
    assert details.new_received_amount is None
    assert details.new_status is None


def test_update_ticket_saves_without_changes_when_extras_empty(details: TicketPaymentVerificationDetails) -> None:
    extras = {"ticket_payment_verification_details_extras": {}}

    result = update_ticket_payment_verification_service(details.ticket, extras, {})

    details.refresh_from_db()
    assert result == details.ticket
    assert details.new_received_amount is None
    assert details.new_status is None
