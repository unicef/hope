from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.forms.models import inlineformset_factory
from django.test import Client, TestCase
from django.urls import reverse

import responses
from django_webtest import WebTest

from hct_mis_api.apps.account.admin import UserRoleAdminForm, UserRoleInlineFormSet
from hct_mis_api.apps.account.fixtures import RoleFactory, UserFactory
from hct_mis_api.apps.account.models import IncompatibleRoles, Role, User, UserRole
from hct_mis_api.apps.core.models import BusinessArea


class UserImportCSVTest(WebTest):
    def setUp(self):
        call_command("loadbusinessareas")
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.user = UserFactory(is_superuser=True, is_staff=True)
        self.role = RoleFactory(name="NoAccess")
        # self.user.set_password('123')
        # self.user.save()
        # self.client = Client()
        # self.client.login(username=self.user.username, password='123')

    @responses.activate
    def test_import_csv(self):
        responses.add(responses.POST, f"{settings.KOBO_KF_URL}/authorized_application/users/", json={}, status=201)

        url = reverse("admin:account_user_import_csv")
        with (Path(__file__).parent / "users.csv").open("r") as fp:
            res = self.app.get(url, user=self.user)
            res.form["file"] = ("users.csv", (Path(__file__).parent / "users.csv").read_bytes())
            res.form["business_area"] = self.business_area.id
            res.form["role"] = self.role.id
            res.form["enable_kobo"] = True
            res.form["enable_cash_assist"] = True
            res = res.form.submit()
            assert res.status_code == 200

            u = User.objects.filter(email="test@example.com").first()
            assert u
            assert u.custom_fields["kobo_username"] == u.username
            assert u.custom_fields["cash_assist_username"] == u.username
