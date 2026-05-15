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


def test_cw_push_payload_correlation_id_maps_to_country_workspace_id(
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
    assert rdi.country_workspace_id == "cw-correlation-abc-123"


def test_cw_push_without_correlation_id_returns_400(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
) -> None:
    response = token_api_client.post(cw_create_url, cw_create_payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert "correlation_id" in response.json()
    assert RegistrationDataImport.objects.filter(name=cw_create_payload["name"]).count() == 0


def test_cw_push_with_blank_correlation_id_returns_400(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
) -> None:
    payload = {**cw_create_payload, "correlation_id": ""}

    response = token_api_client.post(cw_create_url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert "correlation_id" in response.json()


def test_cw_push_duplicate_correlation_id_rejected(
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
    payload = {**cw_create_payload, "correlation_id": "duplicate-id"}

    response = token_api_client.post(cw_create_url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert RegistrationDataImport.objects.filter(country_workspace_id="duplicate-id").count() == 1


def test_cw_push_response_correlation_id_sourced_from_country_workspace_id(
    token_api_client: APIClient,
    cw_create_url: str,
    cw_create_payload: dict,
) -> None:
    payload = {**cw_create_payload, "correlation_id": "cw-roundtrip-xyz"}

    response = token_api_client.post(cw_create_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    body = response.json()
    assert body.get("correlation_id") == "cw-roundtrip-xyz"
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


def test_complete_cw_rdi_enqueues_arrival_hook_on_commit(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    rdi_loading_cw: RegistrationDataImport,
    django_capture_on_commit_callbacks: Any,
) -> None:
    url = reverse("api:rdi-complete", args=[user_business_area.slug, str(rdi_loading_cw.id)])

    with patch("hope.api.endpoints.rdi.base.classify_findings_and_schedule_merge_async_task") as mock_enqueue:
        with django_capture_on_commit_callbacks(execute=True):
            response = token_api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_200_OK, str(response.json())
    rdi_loading_cw.refresh_from_db()
    assert rdi_loading_cw.status == RegistrationDataImport.MERGE_SCHEDULED
    mock_enqueue.assert_called_once()
    enqueued_rdi = mock_enqueue.call_args.args[0]
    assert enqueued_rdi.id == rdi_loading_cw.id


def test_complete_non_cw_rdi_does_not_enqueue_arrival_hook(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    rdi_loading_non_cw: RegistrationDataImport,
    django_capture_on_commit_callbacks: Any,
) -> None:
    url = reverse("api:rdi-complete", args=[user_business_area.slug, str(rdi_loading_non_cw.id)])

    with patch("hope.api.endpoints.rdi.base.classify_findings_and_schedule_merge_async_task") as mock_enqueue:
        with django_capture_on_commit_callbacks(execute=True):
            response = token_api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_200_OK, str(response.json())
    rdi_loading_non_cw.refresh_from_db()
    assert rdi_loading_non_cw.status == RegistrationDataImport.IN_REVIEW
    mock_enqueue.assert_not_called()
