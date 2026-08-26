from typing import Any, Callable

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.constants import PRIORITY_HIGH, PRIORITY_LOW
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def attacker_business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def attacker_program(attacker_business_area: BusinessArea) -> Program:
    return ProgramFactory(status=Program.ACTIVE, business_area=attacker_business_area)


@pytest.fixture
def attacker(
    attacker_business_area: BusinessArea,
    attacker_program: Program,
    create_user_role_with_permissions: Callable,
) -> User:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCES_UPDATE],
        attacker_business_area,
        attacker_program,
    )
    return user


@pytest.fixture
def authenticated_client(api_client: Callable, attacker: User) -> Any:
    return api_client(attacker)


@pytest.fixture
def victim_program() -> Program:
    return ProgramFactory(
        status=Program.ACTIVE,
        business_area=BusinessAreaFactory(name="Ukraine", slug="ukraine", code="0070"),
    )


@pytest.fixture
def victim_ticket(victim_program: Program) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        business_area=victim_program.business_area,
        status=GrievanceTicket.STATUS_NEW,
        priority=PRIORITY_LOW,
    )
    ticket.programs.add(victim_program)
    return ticket


@pytest.fixture
def bulk_priority_url(attacker_business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-bulk-update-priority",
        kwargs={"business_area_slug": attacker_business_area.slug},
    )


def test_bulk_update_priority_of_ticket_from_other_business_area_is_denied(
    authenticated_client: Any,
    bulk_priority_url: str,
    victim_ticket: GrievanceTicket,
) -> None:
    response = authenticated_client.post(
        bulk_priority_url,
        {"grievance_ticket_ids": [str(victim_ticket.id)], "priority": PRIORITY_HIGH},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.status_code
    victim_ticket.refresh_from_db()
    assert victim_ticket.priority == PRIORITY_LOW
