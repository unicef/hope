from typing import Any, Callable

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FeedbackFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.constants import PRIORITY_HIGH, PRIORITY_LOW
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, Feedback, Household, Individual, Program, User

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
def victim_household(victim_program: Program) -> Household:
    household = HouseholdFactory(
        business_area=victim_program.business_area,
        program=victim_program,
        create_role=False,
    )
    individual = IndividualFactory(
        household=household,
        business_area=victim_program.business_area,
        program=victim_program,
        registration_data_import=household.registration_data_import,
    )
    household.head_of_household = individual
    household.save(update_fields=["head_of_household"])
    return household


@pytest.fixture
def victim_individual(victim_household: Household) -> Individual:
    return victim_household.head_of_household


@pytest.fixture
def victim_feedback(victim_program: Program) -> Feedback:
    return FeedbackFactory(
        business_area=victim_program.business_area,
        program=victim_program,
        created_by=UserFactory(),
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


@pytest.fixture
def list_url(attacker_business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-list",
        kwargs={"business_area_slug": attacker_business_area.slug},
    )


def test_create_referral_ticket_for_individual_from_other_business_area_is_denied(
    authenticated_client: Any,
    list_url: str,
    victim_individual: Individual,
) -> None:
    response = authenticated_client.post(
        list_url,
        {
            "description": "cross business area referral",
            "category": GrievanceTicket.CATEGORY_REFERRAL,
            "consent": True,
            "extras": {"category": {"referral_ticket_extras": {"individual": str(victim_individual.id)}}},
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.status_code
    assert not GrievanceTicket.objects.exists()


def test_create_data_change_ticket_for_individual_from_other_business_area_is_denied(
    authenticated_client: Any,
    list_url: str,
    victim_individual: Individual,
) -> None:
    response = authenticated_client.post(
        list_url,
        {
            "description": "cross business area data change",
            "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
            "issue_type": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            "consent": True,
            "extras": {
                "issue_type": {
                    "individual_data_update_issue_type_extras": {
                        "individual": str(victim_individual.id),
                        "individual_data": {"given_name": "Attacker"},
                    }
                }
            },
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.status_code
    assert not GrievanceTicket.objects.exists()


def test_create_ticket_linked_to_feedback_from_other_business_area_is_denied(
    authenticated_client: Any,
    list_url: str,
    victim_feedback: Feedback,
) -> None:
    response = authenticated_client.post(
        list_url,
        {
            "description": "cross business area feedback link",
            "category": GrievanceTicket.CATEGORY_REFERRAL,
            "consent": True,
            "linked_feedback_id": str(victim_feedback.id),
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.status_code
    victim_feedback.refresh_from_db()
    assert victim_feedback.linked_grievance is None


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
