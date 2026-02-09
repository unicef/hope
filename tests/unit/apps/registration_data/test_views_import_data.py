"""Tests for registration data ImportData and KoboImportData retrieve views."""

from typing import Any

from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    ImportDataFactory,
    KoboImportDataFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, ImportData, Partner, User

pytestmark = pytest.mark.django_db


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
        Permissions.RDI_VIEW_LIST,
        Permissions.RDI_VIEW_DETAILS,
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
def api_client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def api_client_no_permissions(user_no_permissions: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user_no_permissions)
    return client


def test_import_data_retrieve_without_permission(
    api_client_no_permissions: APIClient,
    business_area: BusinessArea,
) -> None:
    import_data = ImportDataFactory(business_area_slug=business_area.slug)

    url = reverse(
        "api:registration-data:import-data-detail",
        args=["afghanistan", import_data.id],
    )
    response = api_client_no_permissions.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_import_data_retrieve(api_client: APIClient, user: User, business_area: BusinessArea) -> None:
    api_client.force_authenticate(user=user)

    import_data = ImportDataFactory(
        business_area_slug=business_area.slug,
        status=ImportData.STATUS_FINISHED,
        validation_errors='[{"row_number": 1, "header": "name", "message": "Name is required"}]',
        error="Test error message",
    )

    url = reverse(
        "api:registration-data:import-data-detail",
        args=["afghanistan", import_data.id],
    )

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == str(import_data.id)
    assert response.data["status"] == import_data.status
    assert response.data["data_type"] == import_data.data_type
    assert response.data["error"] == "Test error message"

    assert "xlsx_validation_errors" in response.data
    validation_errors = response.data["xlsx_validation_errors"]
    assert len(validation_errors) == 1
    assert validation_errors[0]["row_number"] == 1
    assert validation_errors[0]["header"] == "name"
    assert validation_errors[0]["message"] == "Name is required"


def test_kobo_import_data_retrieve_without_permission(
    api_client_no_permissions: APIClient,
    business_area: BusinessArea,
) -> None:
    kobo_import_data = KoboImportDataFactory(business_area_slug=business_area.slug)

    url = reverse(
        "api:registration-data:kobo-import-data-detail",
        args=["afghanistan", kobo_import_data.id],
    )
    response = api_client_no_permissions.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_kobo_import_data_retrieve(api_client: APIClient, user: User, business_area: BusinessArea) -> None:
    api_client.force_authenticate(user=user)

    kobo_import_data = KoboImportDataFactory(
        business_area_slug=business_area.slug,
        status=ImportData.STATUS_FINISHED,
        kobo_asset_id="test_asset_123",
        validation_errors='[{"header": "age", "message": "Age must be a number"}]',
        only_active_submissions=True,
        pull_pictures=False,
    )

    url = reverse(
        "api:registration-data:kobo-import-data-detail",
        args=["afghanistan", kobo_import_data.id],
    )

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == str(kobo_import_data.id)
    assert response.data["status"] == kobo_import_data.status
    assert response.data["kobo_asset_id"] == "test_asset_123"
    assert response.data["only_active_submissions"]
    assert not response.data["pull_pictures"]

    assert "kobo_validation_errors" in response.data
    validation_errors = response.data["kobo_validation_errors"]
    assert len(validation_errors) == 1
    assert validation_errors[0]["header"] == "age"
    assert validation_errors[0]["message"] == "Age must be a number"


def test_import_data_retrieve_different_business_area(api_client: APIClient, user: User) -> None:
    api_client.force_authenticate(user=user)

    import_data = ImportDataFactory(
        business_area_slug="different_area",
        status=ImportData.STATUS_FINISHED,
    )

    url = reverse(
        "api:registration-data:import-data-detail",
        args=["afghanistan", import_data.id],
    )

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_kobo_import_data_retrieve_different_business_area(api_client: APIClient, user: User) -> None:
    api_client.force_authenticate(user=user)

    kobo_import_data = KoboImportDataFactory(
        business_area_slug="different_area",
        status=ImportData.STATUS_FINISHED,
    )

    url = reverse(
        "api:registration-data:kobo-import-data-detail",
        args=["afghanistan", kobo_import_data.id],
    )

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
