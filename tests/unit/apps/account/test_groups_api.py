from typing import Any

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.old_factories.account import PartnerFactory, UserFactory
from extras.test_utils.old_factories.core import create_afghanistan
from hope.apps.account.permissions import Permissions
from hope.models import User

pytestmark = pytest.mark.django_db()


class TestGroupsAPI:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.list_url = "api:account:groups-list"
        self.detail_url = "api:account:groups-detail"
        self.count_url = "api:account:groups-count"
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        content_type_user = ContentType.objects.get_for_model(User)
        content_type_group = ContentType.objects.get_for_model(Group)

        self.perm_view_user = Permission.objects.get_or_create(
            codename="view_user",
            content_type=content_type_user,
            defaults={"name": "Can view user"},
        )[0]
        self.perm_view_group = Permission.objects.get_or_create(
            codename="view_group",
            content_type=content_type_group,
            defaults={"name": "Can view group"},
        )[0]
        self.perm_change_user = Permission.objects.get_or_create(
            codename="change_user",
            content_type=content_type_user,
            defaults={"name": "Can change user"},
        )[0]
        self.perm_change_group = Permission.objects.get_or_create(
            codename="change_group",
            content_type=content_type_group,
            defaults={"name": "Can change group"},
        )[0]
        self.perm_add_user = Permission.objects.get_or_create(
            codename="add_user",
            content_type=content_type_user,
            defaults={"name": "Can add user"},
        )[0]
        self.perm_delete_user = Permission.objects.get_or_create(
            codename="delete_user",
            content_type=content_type_user,
            defaults={"name": "Can delete user"},
        )[0]
        self.perm_add_group = Permission.objects.get_or_create(
            codename="add_group",
            content_type=content_type_group,
            defaults={"name": "Can add group"},
        )[0]

        self.group_viewer = Group.objects.create(name="VIEWER")
        self.group_viewer.permissions.add(self.perm_view_user, self.perm_view_group)

        self.group_approver = Group.objects.create(name="APPROVER")
        self.group_approver.permissions.add(
            self.perm_view_user,
            self.perm_view_group,
            self.perm_change_user,
            self.perm_change_group,
        )

        self.group_admin = Group.objects.create(name="ADMIN")
        self.group_admin.permissions.add(
            self.perm_view_user,
            self.perm_view_group,
            self.perm_change_user,
            self.perm_change_group,
            self.perm_add_user,
            self.perm_delete_user,
            self.perm_add_group,
        )

    def test_list_groups_without_authentication(self) -> None:
        from rest_framework.test import APIClient

        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(reverse(self.list_url))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_groups(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_FINISH],
            business_area=self.afghanistan,
        )
        response = self.api_client.get(reverse(self.list_url))
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert len(results) == 3

        group_names = {result["name"] for result in results}
        assert "APPROVER" in group_names
        assert "VIEWER" in group_names
        assert "ADMIN" in group_names

    def test_retrieve_group_without_authentication(self) -> None:
        from rest_framework.test import APIClient

        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(reverse(self.detail_url, kwargs={"pk": self.group_approver.id}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_group_with_authentication(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_FINISH],
            business_area=self.afghanistan,
        )
        response = self.api_client.get(reverse(self.detail_url, kwargs={"pk": self.group_approver.id}))
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        assert data["name"] == "APPROVER"
        assert data["id"] == self.group_approver.id
        assert len(data["permissions"]) == 4

        permission_codenames = {p["codename"] for p in data["permissions"]}
        assert "view_user" in permission_codenames
        assert "view_group" in permission_codenames
        assert "change_user" in permission_codenames
        assert "change_group" in permission_codenames

        perm_view_user = next(p for p in data["permissions"] if p["codename"] == "view_user")
        assert perm_view_user == {
            "id": self.perm_view_user.id,
            "name": "Can view user",
            "codename": "view_user",
            "app_label": "account",
            "model": "user",
        }

    def test_retrieve_nonexistent_group(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_FINISH],
            business_area=self.afghanistan,
        )
        response = self.api_client.get(reverse(self.detail_url, kwargs={"pk": 999999}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_groups_ordering(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_FINISH],
            business_area=self.afghanistan,
        )
        # Test ascending order
        response = self.api_client.get(reverse(self.list_url) + "?ordering=name")
        assert response.status_code == status.HTTP_200_OK
        names = [result["name"] for result in response.data["results"]]
        assert names == sorted(names)

        # Test descending order
        response = self.api_client.get(reverse(self.list_url) + "?ordering=-name")
        assert response.status_code == status.HTTP_200_OK
        names = [result["name"] for result in response.data["results"]]
        assert names == sorted(names, reverse=True)

    def test_count_groups_without_authentication(self) -> None:
        from rest_framework.test import APIClient

        unauthenticated_client = APIClient()
        count_url = reverse(self.list_url) + "count/"
        response = unauthenticated_client.get(count_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_count_groups(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_FINISH],
            business_area=self.afghanistan,
        )
        response = self.api_client.get(reverse(self.count_url))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
