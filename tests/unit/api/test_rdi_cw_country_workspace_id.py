from typing import Any
from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.models import BusinessArea, Program, RegistrationDataImport, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(business_area: BusinessArea) -> BusinessArea:
    business_area.ingest_source = BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY
    business_area.save(update_fields=["ingest_source"])
    return business_area


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


def test_cw_push_payload_country_workspace_id_maps_to_country_workspace_id(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
    django_assert_num_queries,
) -> None:
    payload = {**cw_create_payload, "country_workspace_id": "cw-correlation-abc-123"}

    with django_assert_num_queries(9):
        response = token_api_client.post(cw_create_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    rdi = RegistrationDataImport.objects.get(id=response.json()["id"])
    assert rdi.country_workspace_id == "cw-correlation-abc-123"


def test_cw_push_without_country_workspace_id_returns_400(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
) -> None:
    response = token_api_client.post(cw_create_url, cw_create_payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert "country_workspace_id" in response.json()
    assert RegistrationDataImport.objects.filter(name=cw_create_payload["name"]).count() == 0


def test_cw_push_with_blank_country_workspace_id_returns_400(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
) -> None:
    payload = {**cw_create_payload, "country_workspace_id": ""}

    response = token_api_client.post(cw_create_url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert "country_workspace_id" in response.json()


@pytest.mark.skip("Talk with CW if we need to validate cw ids unique on our side")
def test_cw_push_duplicate_country_workspace_id_rejected(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        country_workspace_id="duplicate-id",
    )
    payload = {**cw_create_payload, "country_workspace_id": "duplicate-id"}

    response = token_api_client.post(cw_create_url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert RegistrationDataImport.objects.filter(country_workspace_id="duplicate-id").count() == 1


def test_cw_push_response_country_workspace_id_sourced_from_country_workspace_id(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
) -> None:
    payload = {**cw_create_payload, "country_workspace_id": "cw-roundtrip-xyz"}

    response = token_api_client.post(cw_create_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    body = response.json()
    assert body.get("country_workspace_id") == "cw-roundtrip-xyz"
    rdi = RegistrationDataImport.objects.get(id=body["id"])
    assert rdi.country_workspace_id == "cw-roundtrip-xyz"


@pytest.fixture
def rdi_loading_cw(business_area: BusinessArea, program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        number_of_individuals=0,
        number_of_households=0,
        country_workspace_id="cw-complete-correlation-1",
    )


@pytest.fixture
def rdi_loading_non_cw(business_area: BusinessArea, program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        number_of_individuals=0,
        number_of_households=0,
        country_workspace_id=None,
    )


def test_complete_cw_rdi_enqueues_dispatcher_on_commit(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    rdi_loading_cw: RegistrationDataImport,
    django_capture_on_commit_callbacks: Any,
) -> None:
    url = reverse("api:rdi-complete", args=[user_business_area.slug, str(rdi_loading_cw.id)])

    # Completion moves the RDI to MERGE_SCHEDULED and hands off to the dispatcher, which
    # merges the oldest waiting RDI for the program — not necessarily this one.
    with patch("hope.api.endpoints.rdi.base.rdi_dispatcher_task") as mock_dispatch:
        with django_capture_on_commit_callbacks(execute=True):
            response = token_api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_200_OK, str(response.json())
    rdi_loading_cw.refresh_from_db()
    assert rdi_loading_cw.status == RegistrationDataImport.MERGE_SCHEDULED
    mock_dispatch.assert_called_once_with(rdi_loading_cw.program)
