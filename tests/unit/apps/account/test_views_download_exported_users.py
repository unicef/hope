from django.test import Client
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.account.views import download_exported_users
from hope.models import BusinessArea, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def other_business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="ukraine")


@pytest.fixture
def superuser() -> User:
    return UserFactory(is_superuser=True)


@pytest.fixture
def user_without_permission(business_area: BusinessArea) -> User:
    user = UserFactory(is_superuser=False)
    role = RoleFactory(name="Role without user management", permissions=[])
    RoleAssignmentFactory(business_area=business_area, user=user, partner=None, role=role, program=None)
    return user


@pytest.fixture
def user_with_permission_in_other_business_area(other_business_area: BusinessArea) -> User:
    user = UserFactory(is_superuser=False)
    role = RoleFactory(name="User management", permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST.value])
    RoleAssignmentFactory(business_area=other_business_area, user=user, partner=None, role=role, program=None)
    return user


def test_download_exported_users_returns_message_when_no_users(
    client: Client, superuser: User, business_area: BusinessArea
) -> None:
    client.force_login(superuser)
    response = client.get(reverse(download_exported_users, args=[business_area.slug]))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    assert response.content == b"Nothing to export"


def test_download_exported_users_returns_xlsx_when_users_exist(client: Client, business_area: BusinessArea) -> None:
    user = UserFactory(is_superuser=False, first_name="Aaa")
    client.force_login(user)
    role = RoleFactory(name="Some role", permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST.value])
    RoleAssignmentFactory(business_area=business_area, user=user, partner=None, role=role, program=None)

    response = client.get(reverse(download_exported_users, args=[business_area.slug]))

    assert response.status_code == 200
    assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response["Content-Disposition"].startswith(f'attachment; filename="exported_users_{business_area.slug}_')
    assert response["Content-Disposition"].endswith('.xlsx"')
    assert len(response.content) > 0


def test_download_exported_users_returns_403_without_user_management_permission(
    client: Client, user_without_permission: User, business_area: BusinessArea
) -> None:
    client.force_login(user_without_permission)

    response = client.get(reverse(download_exported_users, args=[business_area.slug]))

    assert response.status_code == 403


def test_download_exported_users_returns_403_when_permission_is_granted_in_other_business_area(
    client: Client, user_with_permission_in_other_business_area: User, business_area: BusinessArea
) -> None:
    client.force_login(user_with_permission_in_other_business_area)

    response = client.get(reverse(download_exported_users, args=[business_area.slug]))

    assert response.status_code == 403
