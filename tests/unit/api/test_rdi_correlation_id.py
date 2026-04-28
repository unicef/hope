import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.models import BusinessArea, Program, RegistrationDataImport, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def cw_create_url(user_business_area: BusinessArea) -> str:
    return reverse("api:rdi-create", args=[user_business_area.slug])


@pytest.fixture
def cw_create_payload(program: Program, imported_by_user: User) -> dict:
    return {
        "name": "cw-rdi",
        "collect_data_policy": "FULL",
        "program": str(program.id),
        "imported_by_email": imported_by_user.email,
    }


def test_cw_push_create_rdi_with_correlation_id_persists(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
    django_assert_num_queries,
) -> None:
    payload = {**cw_create_payload, "correlation_id": "cw-correlation-abc-123"}

    with django_assert_num_queries(10):
        response = token_api_client.post(cw_create_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    rdi = RegistrationDataImport.objects.get(id=response.json()["id"])
    assert rdi.correlation_id == "cw-correlation-abc-123"


def test_cw_push_create_rdi_without_correlation_id_returns_400(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
) -> None:
    response = token_api_client.post(cw_create_url, cw_create_payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert "correlation_id" in response.json()
    assert RegistrationDataImport.objects.filter(name=cw_create_payload["name"]).count() == 0


def test_cw_push_create_rdi_with_blank_correlation_id_returns_400(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
) -> None:
    payload = {**cw_create_payload, "correlation_id": ""}

    response = token_api_client.post(cw_create_url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert "correlation_id" in response.json()


def test_cw_push_create_rdi_duplicate_correlation_id_rejected(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        correlation_id="duplicate-id",
    )
    payload = {**cw_create_payload, "correlation_id": "duplicate-id"}

    response = token_api_client.post(cw_create_url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert RegistrationDataImport.objects.filter(correlation_id="duplicate-id").count() == 1


def test_cw_push_create_rdi_response_includes_correlation_id(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
) -> None:
    payload = {**cw_create_payload, "correlation_id": "cw-roundtrip-xyz"}

    response = token_api_client.post(cw_create_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.json().get("correlation_id") == "cw-roundtrip-xyz"
