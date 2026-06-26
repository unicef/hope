from django.test import Client
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.views import download_exported_users
from hope.models import BusinessArea, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user() -> User:
    return UserFactory()


def test_download_exported_users_returns_message_when_no_users(
    client: Client, user: User, business_area: BusinessArea
) -> None:
    client.force_login(user)
    response = client.get(reverse(download_exported_users, args=[business_area.slug]))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    assert response.content == b"Nothing to export"


def test_download_exported_users_returns_xlsx_when_users_exist(client: Client, business_area: BusinessArea) -> None:
    user = UserFactory(is_superuser=False, first_name="Aaa")
    client.force_login(user)
    role = RoleFactory(name="Some role", permissions=[])
    RoleAssignmentFactory(business_area=business_area, user=user, partner=None, role=role, program=None)

    response = client.get(reverse(download_exported_users, args=[business_area.slug]))

    assert response.status_code == 200
    assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response["Content-Disposition"].startswith(f"attachment; filename=exported_users_{business_area.slug}_")
    assert response["Content-Disposition"].endswith(".xlsx")
    assert len(response.content) > 0
