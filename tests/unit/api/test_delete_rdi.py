from typing import Any
from unittest.mock import Mock, patch
import uuid

from django.db import connection
import psycopg2
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
    PendingHouseholdFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.models import (
    APILogEntry,
    BusinessArea,
    Household,
    Individual,
    PendingHousehold,
    Program,
    RegistrationDataImport,
    User,
)
from hope.models.grant import Grant

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(business_area: BusinessArea) -> BusinessArea:
    business_area.ingest_source = BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY
    business_area.save(update_fields=["ingest_source"])
    return business_area


@pytest.mark.parametrize(
    "rdi_status",
    [
        RegistrationDataImport.LOADING,
        RegistrationDataImport.MERGE_SCHEDULED,
        RegistrationDataImport.MERGING,
        RegistrationDataImport.IMPORT_ERROR,
        RegistrationDataImport.MERGE_ERROR,
        RegistrationDataImport.DEDUPLICATION_FAILED,
    ],
)
def test_delete_204_for_non_merged(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
    rdi_status: str,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area, program=program, status=rdi_status, country_workspace_id="cw-204"
    )
    response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    assert response.status_code == status.HTTP_204_NO_CONTENT, str(response.content)
    assert not RegistrationDataImport.objects.filter(id=rdi.id).exists()


def test_delete_409_for_merged(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.MERGED,
        country_workspace_id="cw-merged",
    )
    response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"error": "rdi_already_merged"}
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()


@pytest.mark.django_db(transaction=True)
def test_delete_409_when_merge_holds_row_lock(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.MERGING,
        country_workspace_id="cw-lock",
    )
    db = connection.settings_dict
    locker = psycopg2.connect(
        dbname=db["NAME"],
        user=db["USER"],
        password=db["PASSWORD"],
        host=db["HOST"],
        port=db["PORT"],
    )
    try:
        with locker.cursor() as cur:
            cur.execute(
                f"SELECT id FROM {RegistrationDataImport._meta.db_table} WHERE id = %s FOR UPDATE",
                [str(rdi.id)],
            )
            response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    finally:
        locker.rollback()
        locker.close()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"error": "rdi_merge_in_progress"}
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()


def test_delete_404_for_unknown_rdi(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
) -> None:
    response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(uuid.uuid4())]))
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_404_for_other_ba(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
) -> None:
    other = RegistrationDataImportFactory(
        business_area=BusinessAreaFactory(name="Ukraine"),
        status=RegistrationDataImport.LOADING,
    )
    response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(other.id)]))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert RegistrationDataImport.objects.filter(id=other.id).exists()


def test_delete_cascades_hh_ind(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
    django_assert_num_queries: Any,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-cascade-hh",
    )
    HouseholdFactory(business_area=user_business_area, program=program, registration_data_import=rdi)
    HouseholdFactory(business_area=user_business_area, program=program, registration_data_import=rdi)
    assert Individual.all_objects.filter(registration_data_import=rdi).exists()
    assert Household.all_objects.filter(registration_data_import=rdi).exists()

    with django_assert_num_queries(66):
        response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Individual.all_objects.filter(registration_data_import=rdi).exists()
    assert not Household.all_objects.filter(registration_data_import=rdi).exists()


def test_delete_cascades_people(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-cascade-people",
    )
    PendingHouseholdFactory(
        business_area=user_business_area,
        program=program,
        registration_data_import=rdi,
        collect_type=PendingHousehold.CollectType.SINGLE.value,
    )
    assert Individual.all_objects.filter(registration_data_import=rdi).exists()
    assert Household.all_objects.filter(registration_data_import=rdi).exists()

    response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Individual.all_objects.filter(registration_data_import=rdi).exists()
    assert not Household.all_objects.filter(registration_data_import=rdi).exists()


def test_delete_frees_country_workspace_id_for_recreate(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
    imported_by_user: User,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-reuse-1",
    )
    response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    payload = {
        "name": "recreated",
        "collect_data_policy": "FULL",
        "program": str(program.id),
        "imported_by_email": imported_by_user.email,
        "country_workspace_id": "cw-reuse-1",
    }
    resp = token_api_client.post(reverse("api:rdi-create", args=[user_business_area.slug]), payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED, str(resp.json())


def test_delete_frees_people_country_workspace_id_guard(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    cw_id = "cw-person-guard"
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-rdi-guard",
    )
    hh = PendingHouseholdFactory(
        business_area=user_business_area,
        program=program,
        registration_data_import=rdi,
        collect_type=PendingHousehold.CollectType.SINGLE.value,
    )
    head = hh.head_of_household
    head.country_workspace_id = cw_id
    head.save(update_fields=["country_workspace_id"])

    guard = Individual.all_objects.filter(
        is_removed=False,
        withdrawn=False,
        business_area=user_business_area,
        country_workspace_id=cw_id,
    )
    assert guard.exists()

    response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not guard.exists()


@patch("hope.apps.registration_data.services.rdi_removal.remove_elasticsearch_documents_by_matching_ids")
def test_delete_removes_elasticsearch_docs_for_active_program(
    mock_remove_es: Mock,
    token_api_client: APIClient,
    user_business_area: BusinessArea,
) -> None:
    active_program = ProgramFactory(
        business_area=user_business_area,
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
    )
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=active_program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-es",
    )
    HouseholdFactory(business_area=user_business_area, program=active_program, registration_data_import=rdi)

    response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert mock_remove_es.called


@patch("hope.apps.registration_data.services.rdi_removal.remove_elasticsearch_documents_by_matching_ids")
def test_delete_swallows_elasticsearch_failure_and_still_commits(
    mock_remove_es: Mock,
    token_api_client: APIClient,
    user_business_area: BusinessArea,
) -> None:
    mock_remove_es.side_effect = Exception("Elasticsearch is down")
    active_program = ProgramFactory(
        business_area=user_business_area,
        status=Program.ACTIVE,
        biometric_deduplication_enabled=True,
    )
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=active_program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-es-fail",
    )
    HouseholdFactory(business_area=user_business_area, program=active_program, registration_data_import=rdi)

    response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert mock_remove_es.called
    assert not RegistrationDataImport.objects.filter(id=rdi.id).exists()
    assert not Household.all_objects.filter(registration_data_import=rdi).exists()


def test_delete_409_when_protected_dependent(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-protected",
    )
    hh = HouseholdFactory(business_area=user_business_area, program=program, registration_data_import=rdi)
    member = IndividualFactory(
        business_area=user_business_area, program=program, registration_data_import=rdi, household=hh
    )
    other_rdi = RegistrationDataImportFactory(
        business_area=user_business_area, program=program, status=RegistrationDataImport.LOADING
    )
    other_hh = HouseholdFactory(business_area=user_business_area, program=program, registration_data_import=other_rdi)
    other_hh.head_of_household = member
    other_hh.save(update_fields=["head_of_household"])

    response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"error": "rdi_has_dependents"}
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()
    assert Individual.all_objects.filter(id=member.id).exists()


def test_delete_401_without_token(
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area, program=program, status=RegistrationDataImport.LOADING
    )
    client = APIClient()
    response = client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()


def test_delete_401_with_invalid_token(
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area, program=program, status=RegistrationDataImport.LOADING
    )
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token invalid-token")
    response = client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()


def test_delete_403_without_rdi_delete_grant(
    api_token: Any,
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area, program=program, status=RegistrationDataImport.LOADING
    )
    api_token.grants = [Grant.API_RDI_UPLOAD.name]
    api_token.save()
    response = token_api_client.delete(reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)]))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()


def test_delete_writes_api_log_entry(
    api_token: Any,
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-apilog",
    )
    url = reverse("api:rdi-delete", args=[user_business_area.slug, str(rdi.id)])
    response = token_api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    entry = APILogEntry.objects.get(token=api_token, method="DELETE")
    assert entry.url == url
    assert entry.status_code == status.HTTP_204_NO_CONTENT
