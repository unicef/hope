from pathlib import Path

from django.conf import settings
from django.urls import reverse

import responses
from constance.test import override_config
from django_webtest import WebTest

from hct_mis_api.apps.account.admin import (
    get_valid_kobo_username,
)
from hct_mis_api.apps.account.fixtures import (
    PartnerFactory,
    RoleFactory,
    UserFactory,
    UserRoleFactory,
)
from hct_mis_api.apps.account.models import IncompatibleRoles, Role, User
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan


class UserImportCSVTest(WebTest):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)
        cls.role = RoleFactory(name="NoAccess")
        cls.role_2 = Role.objects.create(name="Role_2")
        cls.partner = PartnerFactory(name="Partner1")
        IncompatibleRoles.objects.create(role_one=cls.role, role_two=cls.role_2)

    @responses.activate
    def test_import_csv(self):
        url = reverse("admin:account_user_import_csv")
        res = self.app.get(url, user=self.superuser)
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
        res = self.app.get(url, user=self.superuser)
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

    @responses.activate
    def test_import_csv_detect_incompatible_roles(self):
        u: User = UserFactory(email="test@example.com", partner=self.partner)
        UserRoleFactory(user=u, role=self.role_2, business_area=self.business_area)
        url = reverse("admin:account_user_import_csv")
        res = self.app.get(url, user=self.superuser)
        res.form["file"] = ("users.csv", (Path(__file__).parent / "users.csv").read_bytes())
        res.form["business_area"] = self.business_area.id
        res.form["partner"] = self.partner.id
        res.form["role"] = self.role.id
        res.form["enable_kobo"] = False
        res = res.form.submit()
        assert res.status_code == 200

        assert not u.user_roles.filter(role=self.role, business_area=self.business_area).exists()

    @responses.activate
    def test_import_csv_do_not_change_partner(self):
        partner2 = PartnerFactory(name="Partner2")
        u: User = UserFactory(email="test@example.com", partner=self.partner)  # noqa: F841

        url = reverse("admin:account_user_import_csv")
        res = self.app.get(url, user=self.superuser)
        res.form["file"] = ("users.csv", (Path(__file__).parent / "users.csv").read_bytes())
        res.form["business_area"] = self.business_area.id
        res.form["partner"] = partner2.id
        res.form["role"] = self.role.id
        res.form["enable_kobo"] = False
        res = res.form.submit()
        assert res.status_code == 200
        assert not User.objects.filter(email="test@example.com", partner=partner2).exists()

    @responses.activate
    def test_import_csv_with_username(self):
        url = reverse("admin:account_user_import_csv")
        res = self.app.get(url, user=self.superuser)
        res.form["file"] = ("users2.csv", (Path(__file__).parent / "users2.csv").read_bytes())
        res.form["business_area"] = self.business_area.id
        res.form["partner"] = self.partner.id
        res.form["role"] = self.role.id
        res.form["enable_kobo"] = False
        res = res.form.submit()
        assert res.status_code == 200
        assert User.objects.filter(email="test@example.com", username="test_example1", partner=self.partner).exists()


class UserKoboActionsTest(WebTest):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)
        cls.role = RoleFactory(name="NoAccess")

    @responses.activate
    def test_sync_user(self):
        # responses.add(responses.POST, f"{settings.KOBO_KF_URL}/authorized_application/users/", json={}, status=201)

        url = reverse("admin:account_user_kobo_users_sync")
        res = self.app.get(url, user=self.superuser)
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
        kobo_username = get_valid_kobo_username(self.superuser)
        responses.add(
            responses.GET,
            f"{settings.KOBO_KF_URL}/admin/auth/user/?q={kobo_username}&p=1",
            body=f'action-checkbox. value="111"></td>< field-username <a>{self.superuser.username}</a></td>field-email">{self.superuser.email}</td>',
            status=200,
        )
        responses.add(
            responses.GET,
            f"{settings.KOBO_KF_URL}/admin/auth/user/?q={kobo_username}&p=2",
            body=f'action-checkbox. value="111"></td>< field-username <a>{self.superuser.username}</a></td>field-email">{self.superuser.email}</td>',
            status=200,
        )

        url = reverse("admin:account_user_create_kobo_user", args=[self.superuser.pk])
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 302, res.context["messages"]
        self.superuser.refresh_from_db()
