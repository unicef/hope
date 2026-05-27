import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import APITokenFactory, BusinessAreaFactory, ProgramFactory, UserFactory
from hope.apps.grievance.constants import PRIORITY_HIGH, PRIORITY_NOT_SET, URGENCY_NOT_SET, URGENCY_URGENT
from hope.apps.grievance.models import GrievanceTicket
from hope.models import APIToken, BusinessArea, Program, User
from hope.models.grant import Grant

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def api_token(business_area: BusinessArea) -> APIToken:
    token = APITokenFactory(grants=[Grant.API_BENEFICIARY_TICKET_CREATE.name])
    token.valid_for.set([business_area])
    return token


@pytest.fixture
def authenticated_client(api_token: APIToken) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + api_token.key)
    return client


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def assignee() -> User:
    return UserFactory()


@pytest.fixture
def url(business_area: BusinessArea) -> str:
    return reverse("api:beneficiary-ticket-create", args=[business_area.slug])


def test_create_beneficiary_ticket_minimal(
    authenticated_client: APIClient, url: str, business_area: BusinessArea
) -> None:
    data = {"description": "Test beneficiary ticket description"}

    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, response.json()

    ticket = GrievanceTicket.objects.get(id=response.json()["id"])
    assert ticket.category == GrievanceTicket.CATEGORY_BENEFICIARY
    assert ticket.description == "Test beneficiary ticket description"
    assert ticket.business_area == business_area
    assert ticket.consent is True
    assert ticket.status == GrievanceTicket.STATUS_NEW
    assert ticket.priority == PRIORITY_NOT_SET
    assert ticket.urgency == URGENCY_NOT_SET
    assert ticket.assigned_to is None

    resp_data = response.json()
    assert "id" in resp_data
    assert resp_data["code"] == ticket.unicef_id
    assert resp_data["category"] == "Beneficiary"
    assert resp_data["business_area"]["slug"] == business_area.slug
    assert resp_data["assigned_to"] is None


def test_create_beneficiary_ticket_all_fields(
    authenticated_client: APIClient, url: str, program: Program, assignee: User
) -> None:
    data = {
        "description": "Full beneficiary ticket",
        "program": str(program.id),
        "priority": PRIORITY_HIGH,
        "urgency": URGENCY_URGENT,
        "assigned_to": str(assignee.id),
    }

    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, response.json()

    ticket = GrievanceTicket.objects.get(id=response.json()["id"])
    assert ticket.description == "Full beneficiary ticket"
    assert ticket.priority == PRIORITY_HIGH
    assert ticket.urgency == URGENCY_URGENT
    assert ticket.assigned_to == assignee
    assert program in ticket.programs.all()

    resp_data = response.json()
    assert resp_data["assigned_to"]["id"] == str(assignee.id)
    assert resp_data["assigned_to"]["email"] == assignee.email


def test_create_beneficiary_ticket_missing_description(authenticated_client: APIClient, url: str) -> None:
    data = {}

    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "description" in response.json()


def test_create_beneficiary_ticket_unauthorized(url: str, api_token: APIToken) -> None:
    api_token.grants = []
    api_token.save()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + api_token.key)

    data = {"description": "Should fail"}
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_beneficiary_ticket_invalid_business_area(authenticated_client: APIClient) -> None:
    url = reverse("api:beneficiary-ticket-create", args=["nonexistent-business-area"])
    data = {"description": "Should fail"}

    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND
