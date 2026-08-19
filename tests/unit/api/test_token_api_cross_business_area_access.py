"""Cross business area scoping of the token api (GHSA-2xf8-jjc2-9pmv).

A token is valid for the business area of the url path, while a program referenced by id in the
request body is loaded globally. These tests pin the program of another business area to the same
failure as a program that does not exist.
"""

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import APITokenFactory, BusinessAreaFactory, ProgramFactory
from hope.apps.grievance.models import GrievanceTicket
from hope.models import APIToken, BusinessArea, Program, RegistrationDataImport, User
from hope.models.grant import Grant

pytestmark = pytest.mark.django_db


@pytest.fixture
def beneficiary_ticket_client(business_area: BusinessArea) -> APIClient:
    token: APIToken = APITokenFactory(grants=[Grant.API_BENEFICIARY_TICKET_CREATE.name])
    token.valid_for.set([business_area])
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return client


@pytest.fixture
def other_business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Ukraine", slug="ukraine", code="0070")


@pytest.fixture
def other_program(other_business_area: BusinessArea) -> Program:
    return ProgramFactory(status=Program.ACTIVE, business_area=other_business_area)


def test_create_rdi_for_program_from_other_business_area_is_denied(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    other_program: Program,
    imported_by_user: User,
) -> None:
    url = reverse("api:rdi-create", args=[user_business_area.slug])

    response = token_api_client.post(
        url,
        {
            "name": "cross business area rdi",
            "program": str(other_program.id),
            "imported_by_email": imported_by_user.email,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert "program" in response.json()
    assert not RegistrationDataImport.objects.exists()


def test_upload_rdi_for_program_from_other_business_area_is_denied(
    token_api_client: APIClient,
    upload_url: str,
    other_program: Program,
) -> None:
    response = token_api_client.post(
        upload_url,
        {"name": "cross business area upload", "program": str(other_program.id), "households": []},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert "program" in str(response.json())
    assert not RegistrationDataImport.objects.exists()


def test_create_beneficiary_ticket_for_program_from_other_business_area_is_denied(
    beneficiary_ticket_client: APIClient,
    business_area: BusinessArea,
    other_program: Program,
) -> None:
    url = reverse("api:beneficiary-ticket-create", args=[business_area.slug])

    response = beneficiary_ticket_client.post(
        url,
        {"description": "cross business area ticket", "program": str(other_program.id)},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert "program" in response.json()
    assert not GrievanceTicket.objects.exists()
