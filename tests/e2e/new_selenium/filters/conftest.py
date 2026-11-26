from typing import NamedTuple

import pytest

from extras.test_utils.factories import (
    GrievanceTicketFactory,
    HouseholdFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, PaymentPlan, Program


class SearchPair(NamedTuple):
    """Two rows of one list: searching for `shown` must hide `hidden`."""

    shown: str
    hidden: str


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(name="Filters Programme", status=Program.ACTIVE, business_area=business_area)


@pytest.fixture
def rdi_pair(program: Program) -> SearchPair:
    first, second = (
        RegistrationDataImportFactory(name=name, program=program, business_area=program.business_area)
        for name in ("RDI Alpha", "RDI Beta")
    )
    return SearchPair(first.name, second.name)


@pytest.fixture
def target_population_pair(program: Program) -> SearchPair:
    first, second = (
        PaymentPlanFactory(
            name=name,
            business_area=program.business_area,
            program_cycle=program.cycles.first(),
            status=PaymentPlan.Status.TP_OPEN,
        )
        for name in ("TP Alpha", "TP Beta")
    )
    return SearchPair(first.name, second.name)


@pytest.fixture
def payment_plan_pair(program: Program) -> SearchPair:
    first, second = (
        PaymentPlanFactory(
            business_area=program.business_area,
            program_cycle=program.cycles.first(),
            status=PaymentPlan.Status.ACCEPTED,
        )
        for _ in range(2)
    )
    return SearchPair(first.unicef_id, second.unicef_id)


@pytest.fixture
def verification_pair(program: Program) -> SearchPair:
    plans = [
        PaymentPlanFactory(
            business_area=program.business_area,
            program_cycle=program.cycles.first(),
            status=PaymentPlan.Status.FINISHED,
        )
        for _ in range(2)
    ]
    for plan in plans:
        PaymentVerificationPlanFactory(payment_plan=plan)
    return SearchPair(plans[0].unicef_id, plans[1].unicef_id)


@pytest.fixture
def grievance_ticket_pair(program: Program) -> SearchPair:
    tickets = [
        GrievanceTicketFactory(
            business_area=program.business_area, category=GrievanceTicket.CATEGORY_REFERRAL, issue_type=None
        )
        for _ in range(2)
    ]
    for ticket in tickets:
        ticket.programs.add(program)
        ticket.refresh_from_db()
    return SearchPair(tickets[0].unicef_id, tickets[1].unicef_id)


@pytest.fixture
def household_pair(program: Program) -> SearchPair:
    first, second = (HouseholdFactory(business_area=program.business_area, program=program) for _ in range(2))
    return SearchPair(first.unicef_id, second.unicef_id)
