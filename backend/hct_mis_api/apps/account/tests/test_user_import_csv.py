from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.forms.models import inlineformset_factory
from django.test import Client, TestCase
from django.urls import reverse

import responses
from constance import config
from constance.test import override_config
from django_webtest import WebTest

from hct_mis_api.apps.account.admin import (
    UserRoleAdminForm,
    UserRoleInlineFormSet,
    get_valid_kobo_username,
)
from hct_mis_api.apps.account.fixtures import PartnerFactory, RoleFactory, UserFactory
from hct_mis_api.apps.account.models import IncompatibleRoles, Role, User, UserRole
from hct_mis_api.apps.core.models import BusinessArea


class UserImportCSVTest(WebTest):
    def setUp(self):
        call_command("loadbusinessareas")
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.user: User = UserFactory(is_superuser=True, is_staff=True)
        self.role = RoleFactory(name="NoAccess")
        self.partner = PartnerFactory(name="Partner1")
        # self.user.set_password('123')
        # self.user.save()
        # self.client = Client()
        # self.client.login(username=self.user.username, password='123')

    @responses.activate
    def test_import_csv(self):
        url = reverse("admin:account_user_import_csv")
        with (Path(__file__).parent / "users.csv").open("r") as fp:
            res = self.app.get(url, user=self.user)
            res.form["file"] = ("users.csv", (Path(__file__).parent / "users.csv").read_bytes())
            res.form["business_area"] = self.business_area.id
            res.form["partner"] = self.partner.id
            res.form["role"] = self.role.id
            res.form["enable_kobo"] = False
            res = res.form.submit()
            assert res.status_code == 200

            u = User.objects.filter(email="test@example.com", partner=self.partner).first()
            assert u, "User not found"

    @responses.activate
    def test_import_csv_with_kobo(self):
        responses.add(responses.POST, f"{settings.KOBO_KF_URL}/authorized_application/users/", json={}, status=201)

        url = reverse("admin:account_user_import_csv")
        with (Path(__file__).parent / "users.csv").open("r") as fp:
            res = self.app.get(url, user=self.user)
            res.form["file"] = ("users.csv", (Path(__file__).parent / "users.csv").read_bytes())
            res.form["business_area"] = self.business_area.id
            res.form["partner"] = self.partner.id
            res.form["role"] = self.role.id
            res.form["enable_kobo"] = True
            res = res.form.submit()
            assert res.status_code == 200

            u = User.objects.filter(email="test@example.com", partner=self.partner).first()
            assert u, "User not found"
            assert u.custom_fields["kobo_username"] == u.username


class UserKoboActionsTest(WebTest):
    def setUp(self):
        call_command("loadbusinessareas")
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.user: User = UserFactory(is_superuser=True, is_staff=True)
        self.role = RoleFactory(name="NoAccess")

    @responses.activate
    def test_sync_user(self):
        # responses.add(responses.POST, f"{settings.KOBO_KF_URL}/authorized_application/users/", json={}, status=201)

        url = reverse("admin:account_user_kobo_users_sync")
        res = self.app.get(url, user=self.user)
        assert res.status_code == 200

    @responses.activate
    @override_config(KOBO_ADMIN_CREDENTIALS="kobo_admin:pwd")
    def test_create_kobo_user(self):
        responses.add(responses.POST, f"{settings.KOBO_KF_URL}/authorized_application/users/", json={}, status=201)
        responses.add(
            responses.POST,
            f"{settings.KOBO_KF_URL}/admin/login/",
            headers={"Location": "https://kf-hope.unitst.org/admin/"},
            status=302,
        )
        responses.add(
            responses.GET,
            f"{settings.KOBO_KF_URL}/admin/login/",
            body='<input type="text" name="csrfmiddlewaretoken" value="1111">',
            status=200,
        )
        kobo_username = get_valid_kobo_username(self.user)
        responses.add(
            responses.GET,
            f"{settings.KOBO_KF_URL}/admin/auth/user/?q={kobo_username}&p=1",
            body=f'action-checkbox. value="111"></td>< field-username <a>{self.user.username}</a></td>field-email">{self.user.email}</td>',
            status=200,
        )
        responses.add(
            responses.GET,
            f"{settings.KOBO_KF_URL}/admin/auth/user/?q={kobo_username}&p=2",
            body=f'action-checkbox. value="111"></td>< field-username <a>{self.user.username}</a></td>field-email">{self.user.email}</td>',
            status=200,
        )

        url = reverse("admin:account_user_create_kobo_user", args=[self.user.pk])
        res = self.app.get(url, user=self.user)
        assert res.status_code == 302, res.context["messages"]
        self.user.refresh_from_db()
        assert self.user.custom_fields["kobo_username"] == self.user.username
