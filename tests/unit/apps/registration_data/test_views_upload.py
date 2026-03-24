"""Tests for registration data upload views."""

from contextlib import contextmanager
from typing import Any, Callable, Generator
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DEFAULT_DB_ALIAS, connections
from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, ImportData, KoboImportData, Partner, Program, User

pytestmark = pytest.mark.django_db


@contextmanager
def capture_on_commit_callbacks(
    *, using: str = DEFAULT_DB_ALIAS, execute: bool = False
) -> Generator[list[Callable[[], None]], None, None]:
    callbacks: list[Callable[[], None]] = []
    start_count = len(connections[using].run_on_commit)
    try:
        yield callbacks
    finally:
        while True:
            callback_count = len(connections[using].run_on_commit)
            for _, callback, _ in connections[using].run_on_commit[start_count:]:
                callbacks.append(callback)
                if execute:
                    callback()

            if callback_count == len(connections[using].run_on_commit):
                break
            start_count = callback_count


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def unicef_partner(db: Any) -> Partner:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def unicef_hq(unicef_partner: Partner) -> Partner:
    return PartnerFactory(name="UNICEF HQ", parent=unicef_partner)


@pytest.fixture
def user(unicef_hq: Partner, business_area: BusinessArea) -> User:
    user_permissions = [
        Permissions.RDI_IMPORT_DATA,
    ]
    user = UserFactory(
        username="Hope_Test_DRF",
        password="HopePass",
        partner=unicef_hq,
        is_superuser=True,
    )
    permission_list = [perm.value for perm in user_permissions]
    role = RoleFactory(name="TestName", permissions=permission_list)
    RoleAssignmentFactory(user=user, role=role, business_area=business_area)
    return user


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="Test Partner")


@pytest.fixture
def user_no_permissions(partner: Partner) -> User:
    return UserFactory(
        username="Hope_Test_DRF",
        password="HopePass",
        partner=partner,
        is_superuser=False,
    )


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        name="Test Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )


@pytest.fixture
def api_client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def api_client_no_permissions(user_no_permissions: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user_no_permissions)
    return client


def test_upload_xlsx_file_without_permission(
    api_client_no_permissions: APIClient,
    program: Program,
) -> None:
    url = reverse(
        "api:registration-data:import-data-upload-upload-xlsx-file",
        args=["afghanistan", program.slug],
    )

    file_content = b"test xlsx content"
    uploaded_file = SimpleUploadedFile(
        "test_data.xlsx",
        file_content,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response = api_client_no_permissions.post(url, {"file": uploaded_file}, format="multipart")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch("hope.apps.registration_data.celery_tasks.validate_xlsx_import_task.delay")
def test_upload_xlsx_file(
    mock_validate_task: Mock, api_client: APIClient, user: User, program: Program, business_area: BusinessArea
) -> None:
    url = reverse(
        "api:registration-data:import-data-upload-upload-xlsx-file",
        args=["afghanistan", program.slug],
    )

    # Create a test XLSX file
    file_content = b"test xlsx content"
    uploaded_file = SimpleUploadedFile(
        "test_data.xlsx",
        file_content,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    with capture_on_commit_callbacks(execute=True):
        response = api_client.post(url, {"file": uploaded_file}, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED

    # Check response contains required fields
    assert "id" in response.data
    assert "status" in response.data
    assert response.data["data_type"] == ImportData.XLSX

    # Check ImportData was created
    import_data = ImportData.objects.get(id=response.data["id"])
    assert import_data.status == ImportData.STATUS_PENDING
    assert import_data.data_type == ImportData.XLSX
    assert import_data.business_area_slug == business_area.slug
    assert import_data.created_by_id == user.id

    # Check celery task was called
    mock_validate_task.assert_called_once()
    call_args = mock_validate_task.call_args[0]
    assert call_args[0] == import_data.id
    assert call_args[1] == str(program.id)


def test_save_kobo_import_data_without_permission(
    api_client_no_permissions: APIClient,
    program: Program,
) -> None:
    url = reverse(
        "api:registration-data:kobo-import-data-upload-save-kobo-import-data",
        args=["afghanistan", program.slug],
    )

    data = {
        "uid": "test_kobo_asset_123",
        "only_active_submissions": True,
        "pull_pictures": False,
    }
    response = api_client_no_permissions.post(url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch("hope.apps.registration_data.celery_tasks.pull_kobo_submissions_task.delay")
def test_save_kobo_import_data(
    mock_pull_task: Mock, api_client: APIClient, user: User, program: Program, business_area: BusinessArea
) -> None:
    url = reverse(
        "api:registration-data:kobo-import-data-upload-save-kobo-import-data",
        args=["afghanistan", program.slug],
    )

    data = {
        "uid": "test_kobo_asset_123",
        "only_active_submissions": True,
        "pull_pictures": False,
    }

    with capture_on_commit_callbacks(execute=True):
        response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    # Check response contains required fields
    assert "id" in response.data
    assert "status" in response.data
    assert response.data["kobo_asset_id"] == "test_kobo_asset_123"
    assert response.data["only_active_submissions"]
    assert not response.data["pull_pictures"]

    # Check KoboImportData was created
    kobo_import_data = KoboImportData.objects.get(id=response.data["id"])
    assert kobo_import_data.status == ImportData.STATUS_PENDING
    assert kobo_import_data.data_type == ImportData.JSON
    assert kobo_import_data.kobo_asset_id == "test_kobo_asset_123"
    assert kobo_import_data.only_active_submissions
    assert not kobo_import_data.pull_pictures
    assert kobo_import_data.business_area_slug == business_area.slug
    assert kobo_import_data.created_by_id == user.id

    # Check celery task was called
    mock_pull_task.assert_called_once()
    call_args = mock_pull_task.call_args[0]
    assert call_args[0] == kobo_import_data.id
    assert call_args[1] == str(program.id)
