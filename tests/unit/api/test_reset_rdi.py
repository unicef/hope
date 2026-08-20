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
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.registration_data.celery_tasks import remove_rdi_population_async_task_action
from hope.models import (
    APILogEntry,
    AsyncRetryJob,
    BusinessArea,
    Program,
    RegistrationDataImport,
    User,
)
from hope.models.grant import Grant

pytestmark = pytest.mark.django_db

CALLBACK_URL = "https://cw.example.com/api/rdi/callback/abc123"
SIGNED_TOKEN = "signed-token-abc123"


@pytest.fixture
def business_area(business_area: BusinessArea) -> BusinessArea:
    business_area.ingest_source = BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY
    business_area.save(update_fields=["ingest_source"])
    return business_area


def _reset_url(ba: BusinessArea, rdi_id: str) -> str:
    return reverse("api:rdi-reset", args=[ba.slug, rdi_id])


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"callback_url": CALLBACK_URL},
        {"signed_token": SIGNED_TOKEN},
    ],
)
def test_reset_400_missing_required_field(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
    body: dict,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-400",
    )
    response = token_api_client.post(_reset_url(user_business_area, str(rdi.id)), body, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.content)


@pytest.mark.parametrize(
    "callback_url",
    [
        "",
        "not-a-url",
        "example.com/cb",
        "http://",
        "https:// cw/cb",
        "javascript:alert(1)",
        "ftp://cw/cb",
        "ftps://cw/cb",
        "https://cw//api//cb",
    ],
)
def test_reset_400_invalid_callback_url(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
    callback_url: str,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-400-inv",
    )
    response = token_api_client.post(
        _reset_url(user_business_area, str(rdi.id)), {"callback_url": callback_url}, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.content)


@patch("hope.api.endpoints.rdi.base.rdi_dispatcher_task")
@patch("hope.api.endpoints.rdi.base.remove_rdi_population_async_task")
def test_reset_202_schedules_fresh(
    enqueue: Mock,
    dispatcher: Mock,
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    enqueue.return_value = Mock()  # a live job was scheduled
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-202",
    )
    response = token_api_client.post(
        _reset_url(user_business_area, str(rdi.id)),
        {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN},
        format="json",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED, str(response.content)
    assert response.json()["status"] == RegistrationDataImport.DELETE_SCHEDULED
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()  # enqueue only, no inline wipe
    enqueue.assert_called_once_with(rdi, callback_url=CALLBACK_URL, signed_token=SIGNED_TOKEN)
    # the RDI left the merge queue, so the next one waiting behind it must be picked up
    dispatcher.assert_called_once_with(program)


@patch("hope.api.endpoints.rdi.base.rdi_dispatcher_task")
@patch("hope.api.endpoints.rdi.base.remove_rdi_population_async_task")
def test_reset_202_idempotent_when_live_job(
    enqueue: Mock,
    dispatcher: Mock,
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    enqueue.return_value = None  # requeue -> None: a live wipe already backs this RDI
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.DELETE_SCHEDULED,  # a wipe is already in flight for this row
        country_workspace_id="cw-live",
    )
    response = token_api_client.post(
        _reset_url(user_business_area, str(rdi.id)),
        {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN},
        format="json",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED, str(response.content)
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DELETE_SCHEDULED
    enqueue.assert_called_once_with(rdi, callback_url=CALLBACK_URL, signed_token=SIGNED_TOKEN)
    # the first reset already advanced the queue; this one is a no-op
    dispatcher.assert_not_called()


@patch("hope.api.endpoints.rdi.base.rdi_dispatcher_task")
def test_reset_409_for_merged(
    dispatcher: Mock,
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
    response = token_api_client.post(
        _reset_url(user_business_area, str(rdi.id)),
        {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN},
        format="json",
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"error": "rdi_already_merged"}
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()
    dispatcher.assert_not_called()


@pytest.mark.django_db(transaction=True)
def test_reset_409_when_merge_holds_row_lock(
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
            response = token_api_client.post(
                _reset_url(user_business_area, str(rdi.id)),
                {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN},
                format="json",
            )
    finally:
        locker.rollback()
        locker.close()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"error": "rdi_merge_in_progress"}
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()


def test_reset_404_for_unknown_rdi(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
) -> None:
    response = token_api_client.post(
        _reset_url(user_business_area, str(uuid.uuid4())),
        {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN},
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_reset_404_for_other_ba(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
) -> None:
    other = RegistrationDataImportFactory(
        business_area=BusinessAreaFactory(name="Ukraine"),
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-other-ba",
    )
    response = token_api_client.post(
        _reset_url(user_business_area, str(other.id)),
        {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN},
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert RegistrationDataImport.objects.filter(id=other.id).exists()


def test_reset_404_for_non_cw_managed(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id=None,
    )
    response = token_api_client.post(
        _reset_url(user_business_area, str(rdi.id)),
        {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN},
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()


def test_reset_401_without_token(
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area, program=program, status=RegistrationDataImport.LOADING
    )
    client = APIClient()
    response = client.post(
        _reset_url(user_business_area, str(rdi.id)),
        {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()


def test_reset_401_invalid_token(
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area, program=program, status=RegistrationDataImport.LOADING
    )
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token invalid-token")
    response = client.post(
        _reset_url(user_business_area, str(rdi.id)),
        {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()


def test_reset_403_without_rdi_delete_grant(
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
    response = token_api_client.post(
        _reset_url(user_business_area, str(rdi.id)),
        {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert RegistrationDataImport.objects.filter(id=rdi.id).exists()


@patch("hope.api.endpoints.rdi.base.remove_rdi_population_async_task")
def test_reset_writes_api_log_entry(
    enqueue: Mock,
    api_token: Any,
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    enqueue.return_value = Mock()
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id="cw-apilog",
    )
    url = _reset_url(user_business_area, str(rdi.id))
    response = token_api_client.post(url, {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN}, format="json")
    assert response.status_code == status.HTTP_202_ACCEPTED

    entry = APILogEntry.objects.get(token=api_token, method="POST")
    assert entry.url == url
    assert entry.status_code == status.HTTP_202_ACCEPTED


def test_reset_frees_country_workspace_id_for_recreate(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
    imported_by_user: User,
) -> None:
    cw_id = "cw-reuse-1"
    rdi = RegistrationDataImportFactory(
        business_area=user_business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        country_workspace_id=cw_id,
    )

    with patch("hope.api.endpoints.rdi.base.remove_rdi_population_async_task") as enqueue:
        enqueue.return_value = Mock()
        reset = token_api_client.post(
            _reset_url(user_business_area, str(rdi.id)),
            {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN},
            format="json",
        )
    assert reset.status_code == status.HTTP_202_ACCEPTED, str(reset.content)

    job = AsyncRetryJob(
        config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN}
    )
    with (
        patch("hope.apps.registration_data.services.rdi_removal.remove_elasticsearch_documents_by_matching_ids"),
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task"),
    ):
        remove_rdi_population_async_task_action(job)
    assert not RegistrationDataImport.objects.filter(id=rdi.id).exists()

    payload = {
        "name": "recreated",
        "collect_data_policy": "FULL",
        "program": str(program.id),
        "imported_by_email": imported_by_user.email,
        "country_workspace_id": cw_id,
    }
    recreate = token_api_client.post(reverse("api:rdi-create", args=[user_business_area.slug]), payload, format="json")
    assert recreate.status_code == status.HTTP_201_CREATED, str(recreate.json())
