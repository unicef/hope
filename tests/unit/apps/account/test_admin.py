import json
from typing import Any, Dict
from unittest.mock import patch
from urllib.parse import unquote

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.template.response import TemplateResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

import pytest
from django_webtest import DjangoTestApp

from hct_mis_api.apps.account.admin.ad import ADUSerMixin
from hct_mis_api.apps.account.fixtures import PartnerFactory, RoleFactory, UserFactory
from hct_mis_api.apps.account.models import Partner, Role, User
from hct_mis_api.apps.core.models import BusinessArea


@pytest.fixture()
def superuser(request: pytest.FixtureRequest, partner_unicef: Partner) -> User:
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture()
def role(request: pytest.FixtureRequest) -> Role:
    return RoleFactory(name="Role")


def test_role_perm_matrix(django_app: DjangoTestApp, superuser: pytest.FixtureRequest) -> None:
    url = reverse("admin:account_role_matrix")
    res = django_app.get(url, user=superuser)
    assert res.status_code == 200


def test_role_sync(django_app: DjangoTestApp, superuser: User, role: Role) -> None:
    url = reverse("admin:account_role_dumpdata_qs")
    res = django_app.get(url, user=superuser)
    assert res.status_code == 200
    jres = json.loads(unquote(res.json["data"]))
    models = set([item["model"] for item in jres])
    assert len(models) == 1
    assert models == {"account.role"}


class MockAdmin(ADUSerMixin):
    def get_queryset(self, request: Any) -> QuerySet[User]:
        return User.objects.all()

    def get_common_context(self, request: Any, obj: Any, **kwargs: Any) -> Dict:
        return {}


class ADUserMixinTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.admin = MockAdmin()
        self.user = get_user_model().objects.create(username="Root", email="test@abc.com", is_staff=True)
        self.user.is_superuser = True
        self.user.save()
        self.partner = PartnerFactory(name="Partner_TEST")
        self.business_area = BusinessArea.objects.create(name="AAA", slug="test-aaa")
        self.role = Role.objects.create(name="Basic User")

    def test_load_ad_users_get_request(self) -> None:
        request = self.factory.get("/admin/load_ad_users/")
        request.user = self.user
        response = self.admin.__class__.load_ad_users(self.admin, request)

        self.assertIsInstance(response, TemplateResponse)
        self.assertEqual(response.template_name, "admin/load_users.html")
        self.assertIn("form", response.context_data)

    @patch("hct_mis_api.apps.account.microsoft_graph.MicrosoftGraphAPI.get_user_data")
    @patch("hct_mis_api.apps.account.models.User.objects.bulk_create")
    @patch("hct_mis_api.apps.account.models.UserRole.objects.bulk_create")
    def test_load_ad_users_post_valid(
        self, mock_bulk_create_users: Any, mock_bulk_create_roles: Any, mock_get_user_data: Any
    ) -> None:
        request = self.factory.post(
            "/admin/load_ad_users/",
            {
                "step": "1",
                "emails": "user1@example.com\nuser2@example.com",
                "role": str(self.role.id),
                "partner": str(self.partner.id),
                "business_area": self.business_area.id,
            },
        )
        request.user = self.user
        mock_get_user_data.return_value = {
            "email": "user1@example.com",
            "first_name": "User",
            "last_name": "One",
        }
        response = self.admin.__class__.load_ad_users(self.admin, request)

        self.assertIsInstance(response, TemplateResponse)
        self.assertEqual(response.template_name, "admin/load_users.html")
        self.assertIn("results", response.context_data)
        self.assertEqual(len(response.context_data["results"].created), 2)
        mock_bulk_create_users.assert_called_once()
        mock_bulk_create_roles.assert_called_once()

    @patch("hct_mis_api.apps.account.microsoft_graph.MicrosoftGraphAPI.get_user_data")
    def test_load_ad_users_post_invalid(self, mock_get_user_data: Any) -> None:
        request = self.factory.post("/admin/load_ad_users/", {"step": "1", "emails": ""})
        request.user = self.user
        response = self.admin.__class__.load_ad_users(self.admin, request)
        self.assertIsInstance(response, TemplateResponse)
        self.assertEqual(response.template_name, "admin/load_users.html")
        self.assertIn("form", response.context_data)
        self.assertFalse(response.context_data["form"].is_valid())
