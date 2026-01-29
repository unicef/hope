from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    APITokenFactory,
    BusinessAreaFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, ImportData, Program, RegistrationDataImport, Role, RoleAssignment, User
from hope.models.api_token import APIToken
from hope.models.utils import Grant

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(db, business_area) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def role(db) -> Role:
    return RoleFactory(
        subsystem="API",
        name="GenericImportRole",
        permissions=[Grant.API_GENERIC_IMPORT.name, Permissions.GENERIC_IMPORT_DATA.name],
    )


@pytest.fixture
def role_assignment(db, user, role, business_area) -> RoleAssignment:
    return RoleAssignmentFactory(user=user, role=role, business_area=business_area)


@pytest.fixture
def api_token(db, user, business_area) -> APIToken:
    token = APITokenFactory(user=user, grants=[Grant.API_GENERIC_IMPORT.name])
    token.valid_for.set([business_area])
    return token


@pytest.fixture
def authenticated_api_client(api_token) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {api_token.key}")
    return client


@pytest.fixture
def upload_url(business_area, program) -> str:
    return reverse(
        "api:generic-import:generic-import-upload-upload",
        args=[business_area.slug, program.slug],
    )


@pytest.fixture
def xlsx_file() -> SimpleUploadedFile:
    return SimpleUploadedFile(
        "test.xlsx",
        b"test xlsx content",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@patch("hope.apps.generic_import.celery_tasks.process_generic_import_task.delay")
def test_upload_valid_xlsx_file_creates_import_data_and_rdi_and_schedules_task(
    mock_task, authenticated_api_client, upload_url, xlsx_file, user, business_area, program, role_assignment
):
    with TestCase.captureOnCommitCallbacks(execute=True):
        response = authenticated_api_client.post(upload_url, {"file": xlsx_file}, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED
    assert "import_data_id" in response.data
    assert "rdi_id" in response.data
    assert response.data["import_data_status"] == ImportData.STATUS_PENDING
    assert response.data["rdi_status"] == RegistrationDataImport.IMPORT_SCHEDULED

    import_data = ImportData.objects.get(id=response.data["import_data_id"])
    assert import_data.status == ImportData.STATUS_PENDING
    assert import_data.business_area_slug == business_area.slug
    assert import_data.data_type == ImportData.XLSX
    assert import_data.created_by_id == user.id

    rdi = RegistrationDataImport.objects.get(id=response.data["rdi_id"])
    assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
    assert rdi.business_area == business_area
    assert rdi.program == program
    assert rdi.imported_by == user
    assert rdi.data_source == RegistrationDataImport.XLS
    assert rdi.import_data == import_data

    mock_task.assert_called_once_with(
        registration_data_import_id=str(rdi.id),
        import_data_id=str(import_data.id),
    )


def test_upload_pdf_file_returns_400_with_file_validation_error(authenticated_api_client, upload_url, role_assignment):
    pdf_file = SimpleUploadedFile(
        "document.pdf",
        b"fake pdf content",
        content_type="application/pdf",
    )

    response = authenticated_api_client.post(upload_url, {"file": pdf_file}, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "file" in response.data
    assert "Excel files" in str(response.data["file"])


def test_upload_without_api_generic_import_grant_returns_403(db, business_area, program, xlsx_file):
    user_without_grant = UserFactory()
    token_no_grant = APITokenFactory(
        user=user_without_grant,
        grants=[Grant.API_READ_ONLY.name],
    )
    token_no_grant.valid_for.set([business_area])

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token_no_grant.key}")

    url = reverse(
        "api:generic-import:generic-import-upload-upload",
        args=[business_area.slug, program.slug],
    )

    response = client.post(url, {"file": xlsx_file}, format="multipart")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_upload_file_larger_than_50mb_returns_400(authenticated_api_client, upload_url, role_assignment):
    large_content = b"x" * (51 * 1024 * 1024)
    large_file = SimpleUploadedFile(
        "large.xlsx",
        large_content,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    response = authenticated_api_client.post(upload_url, {"file": large_file}, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "file" in response.data
    assert "50 MB" in str(response.data["file"])


def test_upload_without_authorization_header_returns_403(db, upload_url, xlsx_file):
    client = APIClient()

    response = client.post(upload_url, {"file": xlsx_file}, format="multipart")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_upload_to_business_area_not_in_token_valid_for_returns_404(
    authenticated_api_client, xlsx_file, program, role_assignment
):
    other_ba = BusinessAreaFactory(name="Somalia", slug="somalia")

    url = reverse(
        "api:generic-import:generic-import-upload-upload",
        args=[other_ba.slug, program.slug],
    )

    response = authenticated_api_client.post(url, {"file": xlsx_file}, format="multipart")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_upload_with_nonexistent_program_slug_returns_404(
    authenticated_api_client, business_area, xlsx_file, role_assignment
):
    url = reverse(
        "api:generic-import:generic-import-upload-upload",
        args=[business_area.slug, "nonexistent-program"],
    )

    response = authenticated_api_client.post(url, {"file": xlsx_file}, format="multipart")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_upload_program_from_different_business_area_returns_404(
    authenticated_api_client, api_token, business_area, xlsx_file, role_assignment
):
    other_ba = BusinessAreaFactory(name="Somalia", slug="somalia")
    other_program = ProgramFactory(business_area=other_ba, status=Program.ACTIVE)
    api_token.valid_for.add(other_ba)

    url = reverse(
        "api:generic-import:generic-import-upload-upload",
        args=[business_area.slug, other_program.slug],
    )

    response = authenticated_api_client.post(url, {"file": xlsx_file}, format="multipart")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@patch("hope.apps.generic_import.celery_tasks.process_generic_import_task.delay")
def test_upload_with_session_authentication_succeeds(mock_task, user, upload_url, xlsx_file, role_assignment, client):
    client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")

    with TestCase.captureOnCommitCallbacks(execute=True):
        response = client.post(upload_url, {"file": xlsx_file})

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["import_data_id"]
    assert data["rdi_id"]
    assert mock_task.called
    data = response.json()
    assert data["import_data_id"]
    assert data["rdi_id"]
    assert mock_task.called
