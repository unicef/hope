from pathlib import Path

import responses
from constance.test import override_config
from django.conf import settings
from django.urls import reverse
from django_webtest import WebTest
from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from extras.test_utils.factories.core import create_afghanistan

from hope.admin.account_mixins import get_valid_kobo_username
from hope.models.user import User
from hope.models.incompatible_roles import IncompatibleRoles
from hope.models.role import Role
from hope.models.business_area import BusinessArea


class UserImportCSVTest(WebTest):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)
        cls.role = RoleFactory(name="NoAccess")
        cls.role_2 = Role.objects.create(name="Role_2")
        cls.partner = PartnerFactory(name="Partner1")
        IncompatibleRoles.objects.create(role_one=cls.role, role_two=cls.role_2)

    @responses.activate
    def test_import_csv(self) -> None:
        url = reverse("admin:account_user_import_csv")
        res = self.app.get(url, user=self.superuser)
        res.form["file"] = (
            "users.csv",
            (Path(__file__).parent / "users.csv").read_bytes(),
        )
        res.form["business_area"] = self.business_area.id
        res.form["partner"] = self.partner.id
        res.form["role"] = self.role.id
        res.form["enable_kobo"] = False
        res = res.form.submit()
        assert res.status_code == 200

        u = User.objects.filter(email="test@example.com", partner=self.partner).first()
        assert u, "User not found"

    @responses.activate
    def test_import_csv_with_kobo(self) -> None:
        responses.add(
            responses.POST,
            f"{settings.KOBO_URL}/authorized_application/users/",
            json={},
            status=201,
        )

        url = reverse("admin:account_user_import_csv")
        res = self.app.get(url, user=self.superuser)
        res.form["file"] = (
            "users.csv",
            (Path(__file__).parent / "users.csv").read_bytes(),
        )
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
    def test_import_csv_detect_incompatible_roles(self) -> None:
        u: User = UserFactory(email="test@example.com", partner=self.partner)
        RoleAssignmentFactory(user=u, role=self.role_2, business_area=self.business_area)
        url = reverse("admin:account_user_import_csv")
        res = self.app.get(url, user=self.superuser)
        res.form["file"] = (
            "users.csv",
            (Path(__file__).parent / "users.csv").read_bytes(),
        )
        res.form["business_area"] = self.business_area.id
        res.form["partner"] = self.partner.id
        res.form["role"] = self.role.id
        res.form["enable_kobo"] = False
        res = res.form.submit()
        assert res.status_code == 200

        assert not u.role_assignments.filter(role=self.role, business_area=self.business_area).exists()

    @responses.activate
    def test_import_csv_do_not_change_partner(self) -> None:
        partner2 = PartnerFactory(name="Partner2")
        u: User = UserFactory(email="test@example.com", partner=self.partner)  # noqa: F841

        url = reverse("admin:account_user_import_csv")
        res = self.app.get(url, user=self.superuser)
        res.form["file"] = (
            "users.csv",
            (Path(__file__).parent / "users.csv").read_bytes(),
        )
        res.form["business_area"] = self.business_area.id
        res.form["partner"] = partner2.id
        res.form["role"] = self.role.id
        res.form["enable_kobo"] = False
        res = res.form.submit()
        assert res.status_code == 200
        assert not User.objects.filter(email="test@example.com", partner=partner2).exists()

    @responses.activate
    def test_import_csv_with_username(self) -> None:
        url = reverse("admin:account_user_import_csv")
        res = self.app.get(url, user=self.superuser)
        res.form["file"] = (
            "users2.csv",
            (Path(__file__).parent / "users2.csv").read_bytes(),
        )
        res.form["business_area"] = self.business_area.id
        res.form["partner"] = self.partner.id
        res.form["role"] = self.role.id
        res.form["enable_kobo"] = False
        res = res.form.submit()
        assert res.status_code == 200
        assert User.objects.filter(email="test@example.com", username="test_example1", partner=self.partner).exists()


class UserKoboActionsTest(WebTest):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)
        cls.role = RoleFactory(name="NoAccess")

    @responses.activate
    def test_sync_user(self) -> None:
        url = reverse("admin:account_user_kobo_users_sync")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200

    @responses.activate
    @override_config(KOBO_ADMIN_CREDENTIALS="kobo_admin:pwd")
    def test_create_kobo_user(self) -> None:
        responses.add(
            responses.POST,
            f"{settings.KOBO_URL}/authorized_application/users/",
            json={},
            status=201,
        )
        responses.add(
            responses.POST,
            f"{settings.KOBO_URL}/admin/login/",
            headers={"Location": "https://kobo-hope-trn.unitst.org/admin/"},
            status=302,
        )
        responses.add(
            responses.GET,
            f"{settings.KOBO_URL}/admin/login/",
            body='<input type="text" name="csrfmiddlewaretoken" value="1111">',
            status=200,
        )
        kobo_username = get_valid_kobo_username(self.superuser)
        responses.add(
            responses.GET,
            f"{settings.KOBO_URL}/admin/auth/user/?q={kobo_username}&p=1",
            body=f'action-checkbox. value="111"></td>< field-username <a>'
            f'{self.superuser.username}</a></td>field-email">{self.superuser.email}</td>',
            status=200,
        )
        responses.add(
            responses.GET,
            f"{settings.KOBO_URL}/admin/auth/user/?q={kobo_username}&p=2",
            body=f'action-checkbox. value="111"></td>< field-username <a>{self.superuser.username}'
            f'</a></td>field-email">{self.superuser.email}</td>',
            status=200,
        )

        url = reverse("admin:account_user_create_kobo_user", args=[self.superuser.pk])
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 302, res.context["messages"]
        self.superuser.refresh_from_db()
