"""BE-09 phase 4 — GenericImportUploadViewSet upload blocked for a CW-only business area.

The viewset mixes in ``BusinessAreaIngestAllExceptCWMixin`` on top of ``PermissionsMixin``, so the
CW guard runs after the auth-specific permission (``BaseRestPermission`` for session requests,
``HOPEPermission`` for token requests). For a Country-Workspace-only business area the unsafe
``upload`` POST is denied before the handler body runs, so neither ``ImportData`` nor
``RegistrationDataImport`` is created on either auth path.

Note: this viewset exposes only the ``upload`` POST action (no list/count/retrieve route), so the
plan's "reads stay open" count check does not apply here — there is no read endpoint to keep open.
"""

from typing import Any

from django.core.files.uploadedfile import SimpleUploadedFile
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
from hope.models import BusinessArea, ImportData, Program, RegistrationDataImport, User
from hope.models.api_token import APIToken
from hope.models.business_area import ALL_EXCEPT_CW_INGEST_REJECT_MSG
from hope.models.grant import Grant

pytestmark = pytest.mark.django_db


@pytest.fixture
def cw_only_business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="afghanistan",
        name="Afghanistan",
        ingest_source=BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY,
    )


@pytest.fixture
def program(cw_only_business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=cw_only_business_area, status=Program.ACTIVE)


@pytest.fixture
def upload_url(cw_only_business_area: BusinessArea, program: Program) -> str:
    return reverse(
        "api:generic-import:generic-import-upload-upload",
        args=[cw_only_business_area.slug, program.code],
    )


@pytest.fixture
def xlsx_file() -> SimpleUploadedFile:
    return SimpleUploadedFile(
        "test.xlsx",
        b"test xlsx content",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# --- session auth: BaseRestPermission branch (GENERIC_IMPORT_DATA), then the CW guard ---


@pytest.fixture
def session_user(cw_only_business_area: BusinessArea) -> User:
    user = UserFactory(is_superuser=True)
    role = RoleFactory(
        name="GenericImportRole",
        permissions=[Grant.API_GENERIC_IMPORT.name, Permissions.GENERIC_IMPORT_DATA.name],
    )
    RoleAssignmentFactory(user=user, role=role, business_area=cw_only_business_area)
    return user


@pytest.fixture
def session_api_client(session_user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=session_user)
    return client


def test_upload_blocked_for_cw_only_business_area(
    session_api_client: APIClient,
    upload_url: str,
    xlsx_file: SimpleUploadedFile,
) -> None:
    response = session_api_client.post(upload_url, {"file": xlsx_file}, format="multipart")

    assert response.status_code == status.HTTP_403_FORBIDDEN, str(response.data)
    assert ALL_EXCEPT_CW_INGEST_REJECT_MSG in str(response.data)
    assert ImportData.objects.count() == 0
    assert RegistrationDataImport.objects.count() == 0


# --- token auth: HOPEPermission branch (API_GENERIC_IMPORT grant), then the CW guard ---


@pytest.fixture
def api_token(cw_only_business_area: BusinessArea) -> APIToken:
    user = UserFactory()
    token = APITokenFactory(user=user, grants=[Grant.API_GENERIC_IMPORT.name])
    token.valid_for.set([cw_only_business_area])
    return token


@pytest.fixture
def token_api_client(api_token: APIToken) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {api_token.key}")
    return client


def test_upload_blocked_for_cw_only_via_token_auth(
    token_api_client: APIClient,
    upload_url: str,
    xlsx_file: SimpleUploadedFile,
) -> None:
    response = token_api_client.post(upload_url, {"file": xlsx_file}, format="multipart")

    assert response.status_code == status.HTTP_403_FORBIDDEN, str(response.data)
    assert ImportData.objects.count() == 0
    assert RegistrationDataImport.objects.count() == 0
