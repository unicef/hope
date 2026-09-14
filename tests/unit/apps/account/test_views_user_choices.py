"""Tests for the business-area-independent user choices endpoint."""

from typing import Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import PartnerFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import to_choice_object
from hope.models import USER_STATUS_CHOICES, Partner, Role, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def roles_setup(db: Any) -> None:
    RoleFactory(name="TestRole")
    RoleFactory(name="TestRole2")
    RoleFactory(name="TestRole3")


@pytest.fixture
def authenticated_client(api_client: Any, user: User) -> Any:
    return api_client(user)


def test_get_choices_returns_every_user_choice_list(
    authenticated_client: Any,
    roles_setup: None,
) -> None:
    response = authenticated_client.get(reverse("api:choices-users"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "role_choices": [{"name": role.name, "value": role.id} for role in Role.objects.order_by("name")],
        "status_choices": to_choice_object(USER_STATUS_CHOICES),
    }


def test_get_choices_allows_authenticated_user_without_any_role(authenticated_client: Any) -> None:
    response = authenticated_client.get(reverse("api:choices-users"))

    assert response.status_code == status.HTTP_200_OK
    assert "partner_choices" not in response.data
    assert "partner_choices_temp" not in response.data


def test_get_choices_denies_anonymous_access() -> None:
    response = APIClient().get(reverse("api:choices-users"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_viewset_choices_returns_choices_for_user_with_role(
    authenticated_client: Any,
    create_user_role_with_permissions: Any,
    user: User,
    roles_setup: None,
) -> None:
    afghanistan = BusinessAreaFactory(slug="afghanistan")
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=afghanistan,
    )
    response = authenticated_client.get(
        reverse("api:accounts:users-choices", kwargs={"business_area_slug": afghanistan.slug})
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "role_choices": [{"name": role.name, "value": role.id} for role in Role.objects.order_by("name")],
        "status_choices": to_choice_object(USER_STATUS_CHOICES),
    }
