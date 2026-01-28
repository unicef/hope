"""Tests for Groups API endpoints."""

from typing import Any

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Partner, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area_afg(db: Any) -> BusinessArea:
    return BusinessAreaFactory(
        slug="afghanistan",
        code="0060",
        name="Afghanistan",
    )


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def content_type_user(db: Any) -> ContentType:
    return ContentType.objects.get_for_model(User)


@pytest.fixture
def content_type_group(db: Any) -> ContentType:
    return ContentType.objects.get_for_model(Group)


@pytest.fixture
def perm_view_user(content_type_user: ContentType) -> Permission:
    perm, _ = Permission.objects.get_or_create(
        codename="view_user",
        content_type=content_type_user,
        defaults={"name": "Can view user"},
    )
    return perm


@pytest.fixture
def perm_view_group(content_type_group: ContentType) -> Permission:
    perm, _ = Permission.objects.get_or_create(
        codename="view_group",
        content_type=content_type_group,
        defaults={"name": "Can view group"},
    )
    return perm


@pytest.fixture
def perm_change_user(content_type_user: ContentType) -> Permission:
    perm, _ = Permission.objects.get_or_create(
        codename="change_user",
        content_type=content_type_user,
        defaults={"name": "Can change user"},
    )
    return perm


@pytest.fixture
def perm_change_group(content_type_group: ContentType) -> Permission:
    perm, _ = Permission.objects.get_or_create(
        codename="change_group",
        content_type=content_type_group,
        defaults={"name": "Can change group"},
    )
    return perm


@pytest.fixture
def perm_add_user(content_type_user: ContentType) -> Permission:
    perm, _ = Permission.objects.get_or_create(
        codename="add_user",
        content_type=content_type_user,
        defaults={"name": "Can add user"},
    )
    return perm


@pytest.fixture
def perm_delete_user(content_type_user: ContentType) -> Permission:
    perm, _ = Permission.objects.get_or_create(
        codename="delete_user",
        content_type=content_type_user,
        defaults={"name": "Can delete user"},
    )
    return perm


@pytest.fixture
def perm_add_group(content_type_group: ContentType) -> Permission:
    perm, _ = Permission.objects.get_or_create(
        codename="add_group",
        content_type=content_type_group,
        defaults={"name": "Can add group"},
    )
    return perm


@pytest.fixture
def group_viewer(perm_view_user: Permission, perm_view_group: Permission) -> Group:
    group = Group.objects.create(name="VIEWER")
    group.permissions.add(perm_view_user, perm_view_group)
    return group


@pytest.fixture
def group_approver(
    perm_view_user: Permission,
    perm_view_group: Permission,
    perm_change_user: Permission,
    perm_change_group: Permission,
) -> Group:
    group = Group.objects.create(name="APPROVER")
    group.permissions.add(
        perm_view_user,
        perm_view_group,
        perm_change_user,
        perm_change_group,
    )
    return group


@pytest.fixture
def group_admin(
    perm_view_user: Permission,
    perm_view_group: Permission,
    perm_change_user: Permission,
    perm_change_group: Permission,
    perm_add_user: Permission,
    perm_delete_user: Permission,
    perm_add_group: Permission,
) -> Group:
    group = Group.objects.create(name="ADMIN")
    group.permissions.add(
        perm_view_user,
        perm_view_group,
        perm_change_user,
        perm_change_group,
        perm_add_user,
        perm_delete_user,
        perm_add_group,
    )
    return group


@pytest.fixture
def all_groups(group_viewer: Group, group_approver: Group, group_admin: Group):
    # Ensures all groups are created
    pass


def test_list_groups_without_authentication(all_groups):
    unauthenticated_client = APIClient()
    response = unauthenticated_client.get(reverse("api:account:groups-list"))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_groups(
    api_client: Any,
    user: User,
    business_area_afg: BusinessArea,
    all_groups,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_FINISH],
        business_area=business_area_afg,
    )

    client = api_client(user)
    response = client.get(reverse("api:account:groups-list"))
    assert response.status_code == status.HTTP_200_OK
    results = response.data["results"]
    assert len(results) == 3

    group_names = {result["name"] for result in results}
    assert "APPROVER" in group_names
    assert "VIEWER" in group_names
    assert "ADMIN" in group_names


def test_retrieve_group_without_authentication(group_approver: Group):
    unauthenticated_client = APIClient()
    response = unauthenticated_client.get(reverse("api:account:groups-detail", kwargs={"pk": group_approver.id}))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_retrieve_group_with_authentication(
    api_client: Any,
    user: User,
    business_area_afg: BusinessArea,
    group_approver: Group,
    perm_view_user: Permission,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_FINISH],
        business_area=business_area_afg,
    )

    client = api_client(user)
    response = client.get(reverse("api:account:groups-detail", kwargs={"pk": group_approver.id}))
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    assert data["name"] == "APPROVER"
    assert data["id"] == group_approver.id
    assert len(data["permissions"]) == 4

    permission_codenames = {p["codename"] for p in data["permissions"]}
    assert "view_user" in permission_codenames
    assert "view_group" in permission_codenames
    assert "change_user" in permission_codenames
    assert "change_group" in permission_codenames

    perm_view_user_data = next(p for p in data["permissions"] if p["codename"] == "view_user")
    assert perm_view_user_data == {
        "id": perm_view_user.id,
        "name": "Can view user",
        "codename": "view_user",
        "app_label": "account",
        "model": "user",
    }


def test_retrieve_nonexistent_group(
    api_client: Any,
    user: User,
    business_area_afg: BusinessArea,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_FINISH],
        business_area=business_area_afg,
    )

    client = api_client(user)
    response = client.get(reverse("api:account:groups-detail", kwargs={"pk": 999999}))
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_groups_ordering(
    api_client: Any,
    user: User,
    business_area_afg: BusinessArea,
    all_groups,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_FINISH],
        business_area=business_area_afg,
    )

    client = api_client(user)

    # Test ascending order
    response = client.get(reverse("api:account:groups-list") + "?ordering=name")
    assert response.status_code == status.HTTP_200_OK
    names = [result["name"] for result in response.data["results"]]
    assert names == sorted(names)

    # Test descending order
    response = client.get(reverse("api:account:groups-list") + "?ordering=-name")
    assert response.status_code == status.HTTP_200_OK
    names = [result["name"] for result in response.data["results"]]
    assert names == sorted(names, reverse=True)


def test_count_groups_without_authentication(all_groups):
    unauthenticated_client = APIClient()
    count_url = reverse("api:account:groups-list") + "count/"
    response = unauthenticated_client.get(count_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_count_groups(
    api_client: Any,
    user: User,
    business_area_afg: BusinessArea,
    all_groups,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_FINISH],
        business_area=business_area_afg,
    )

    client = api_client(user)
    response = client.get(reverse("api:account:groups-count"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3
