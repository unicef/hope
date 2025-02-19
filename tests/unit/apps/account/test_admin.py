import json
from typing import Any, Optional, Union
from unittest.mock import MagicMock
from urllib.parse import unquote

from django.contrib.admin.sites import AdminSite
from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory, TestCase
from django.urls import reverse

import pytest
from django_webtest import DjangoTestApp

from hct_mis_api.apps.account.admin.user_role import (
    RoleAssignmentAdmin,
    RoleAssignmentInline,
)
from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hct_mis_api.apps.account.models import Partner, Role, RoleAssignment, User
from hct_mis_api.apps.core.fixtures import create_afghanistan


@pytest.fixture()
def superuser(request: pytest.FixtureRequest, partner_unicef: Partner) -> User:
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture()
def role(request: pytest.FixtureRequest) -> Role:
    return RoleFactory(name="Role")


@pytest.mark.django_db(transaction=True)
def test_role_perm_matrix(django_app: DjangoTestApp, superuser: pytest.FixtureRequest) -> None:
    url = reverse("admin:account_role_matrix")
    res = django_app.get(url, user=superuser)
    assert res.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_role_sync(django_app: DjangoTestApp, superuser: User, role: Role) -> None:
    url = reverse("admin:account_role_dumpdata_qs")
    res = django_app.get(url, user=superuser)
    assert res.status_code == 200
    jres = json.loads(unquote(res.json["data"]))
    models = set([item["model"] for item in jres])
    assert len(models) == 1
    assert models == {"account.role"}


class RoleAssignmentInlineTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = RoleAssignmentInline(parent_model=Partner, admin_site=self.site)

        self.user = UserFactory()
        self.parent = PartnerFactory(name="UNICEF")
        self.partner = PartnerFactory(parent=self.parent)
        self.parent_without_parent = PartnerFactory(parent=None, name="Parent without parent")
        self.business_area = create_afghanistan()
        self.other_ba = BusinessAreaFactory(name="Ukraine")
        self.partner.allowed_business_areas.set([self.business_area])
        self.role = RoleFactory(is_available_for_partner=True)
        self.role_not_available = RoleFactory(is_available_for_partner=False)

    def get_mock_request(self, object_id: Any = None) -> Union[WSGIRequest, WSGIRequest]:
        request = self.factory.get("/")
        request.resolver_match = MagicMock()
        request.resolver_match.kwargs = {"object_id": str(object_id) if object_id else None}
        request.user = MagicMock()
        request.user.can_add_business_area_to_partner = MagicMock(return_value=True)
        return request

    def test_formfield_for_foreignkey_business_area(self) -> None:
        request = self.get_mock_request(object_id=self.partner.id)

        field = self.admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("business_area"), request)
        self.assertIn(self.business_area, field.queryset)
        self.assertNotIn(self.other_ba, field.queryset)

        request = self.get_mock_request(object_id="some not digit string")

        field = self.admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("business_area"), request)
        self.assertIn(self.business_area, field.queryset)
        self.assertIn(self.other_ba, field.queryset)

    def test_formfield_for_foreignkey_role(self) -> None:
        request = self.get_mock_request(object_id=self.partner.id)

        field = self.admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("role"), request)
        self.assertIn(self.role, field.queryset)
        self.assertNotIn(self.role_not_available, field.queryset)

        request = self.get_mock_request(object_id="some not digit string")

        field = self.admin.formfield_for_foreignkey(RoleAssignment._meta.get_field("role"), request)
        self.assertIn(self.role, field.queryset)
        self.assertIn(self.role_not_available, field.queryset)

    def test_has_add_permission(self) -> None:
        request = self.get_mock_request(object_id=self.partner.id)
        self.assertFalse(self.admin.has_add_permission(request, self.partner))

        self.assertFalse(self.admin.has_add_permission(request, self.parent))

        self.assertTrue(self.admin.has_add_permission(request, self.parent_without_parent))

        self.assertTrue(self.admin.has_add_permission(request, self.user))

    def test_has_change_permission(self) -> None:
        request = self.get_mock_request(object_id=self.partner.id)
        self.assertFalse(self.admin.has_change_permission(request, self.partner))

        self.assertTrue(self.admin.has_change_permission(request, self.parent))

        self.assertTrue(self.admin.has_change_permission(request, self.parent_without_parent))

        self.assertTrue(self.admin.has_change_permission(request, self.user))

    def test_has_delete_permission(self) -> None:
        request = self.get_mock_request(object_id=self.partner.id)
        self.assertFalse(self.admin.has_delete_permission(request, self.partner))

        self.assertTrue(self.admin.has_delete_permission(request, self.parent))

        self.assertTrue(self.admin.has_delete_permission(request, self.parent_without_parent))

        self.assertTrue(self.admin.has_delete_permission(request, self.user))


class RoleAssignmentAdminTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = RoleAssignmentAdmin(model=RoleAssignment, admin_site=self.site)

        self.user = UserFactory(username="testuser", is_staff=True)
        self.business_area = create_afghanistan()
        self.role = RoleFactory()
        self.role_assignment = RoleAssignmentFactory(
            user=self.user,
            role=self.role,
            business_area=self.business_area,
        )

    def get_mock_request(self, user: Optional[User] = None) -> Union[WSGIRequest, WSGIRequest]:
        """Helper to create a mock request"""
        request = self.factory.get("/")
        request.user = user if user else self.user
        return request

    def test_get_queryset(self) -> None:
        request = self.get_mock_request()
        queryset = self.admin.get_queryset(request)
        self.assertIn(self.role_assignment, queryset)

    def test_get_actions(self) -> None:
        request = self.get_mock_request()
        actions = self.admin.get_actions(request)
        self.assertIsInstance(actions, dict)

    def test_check_sync_permission(self) -> None:
        request = self.get_mock_request()
        self.assertTrue(self.admin.check_sync_permission(request))

        request.user.is_staff = False
        request.user.save()
        self.assertFalse(self.admin.check_sync_permission(request))

    def test_check_publish_permission(self) -> None:
        request = self.get_mock_request()
        self.assertFalse(self.admin.check_publish_permission(request))
