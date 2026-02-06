import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.old_factories.account import BusinessAreaFactory, UserFactory
from extras.test_utils.old_factories.program import ProgramFactory
from hope.apps.grievance.constants import PRIORITY_HIGH, PRIORITY_NOT_SET, URGENCY_NOT_SET, URGENCY_URGENT
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Program
from hope.models.grant import Grant
from unit.api.factories import APITokenFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def api_token(business_area):
    user = UserFactory()
    token = APITokenFactory(
        user=user,
        grants=[Grant.API_BENEFICIARY_TICKET_CREATE.name],
    )
    token.valid_for.set([business_area])
    return token


@pytest.fixture
def authenticated_client(api_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + api_token.key)
    return client


@pytest.fixture
def program(business_area):
    return ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
    )


@pytest.fixture
def url(business_area):
    return reverse("api:beneficiary-ticket-create", args=[business_area.slug])


def test_create_beneficiary_ticket_minimal(authenticated_client, url, business_area):
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


def test_create_beneficiary_ticket_all_fields(authenticated_client, url, program):
    assignee = UserFactory()
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


def test_create_beneficiary_ticket_with_program(authenticated_client, url, program):
    data = {
        "description": "Ticket with program",
        "program": str(program.id),
    }

    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    ticket = GrievanceTicket.objects.get(id=response.json()["id"])
    assert ticket.programs.count() == 1
    assert ticket.programs.first() == program


def test_create_beneficiary_ticket_missing_description(authenticated_client, url):
    data = {}

    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "description" in response.json()


def test_create_beneficiary_ticket_unauthorized(url, api_token):
    api_token.grants = []
    api_token.save()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + api_token.key)

    data = {"description": "Should fail"}
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_beneficiary_ticket_invalid_business_area(authenticated_client):
    url = reverse("api:beneficiary-ticket-create", args=["nonexistent-business-area"])
    data = {"description": "Should fail"}

    response = authenticated_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND
