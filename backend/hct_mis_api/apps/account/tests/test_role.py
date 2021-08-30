from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from django_webtest import WebTest

from hct_mis_api.apps.account.fixtures import UserFactory, UserRoleFactory
from hct_mis_api.apps.account.models import Role, User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import BusinessArea


class RoleTest(WebTest):
    def setUp(self):
        self.role_1 = Role.objects.create(name="Role_1")
        self.user = UserFactory()
        self.superuser: User = UserFactory(is_superuser=True, is_staff=True)

    def test_user_role_history(self):
        url = reverse("admin:account_role_change", args=[self.role_1.pk])
        res = self.app.get(url, user=self.superuser)
        url = reverse("admin:account_role_change", args=[self.role_1.pk])
        res.form["permissions"] = ["RDI_VIEW_LIST"]
        res.form.submit().follow()

        res = self.app.get(url, user=self.superuser)
        res.form["permissions"] = ["RDI_IMPORT_DATA"]
        res.form.submit().follow()

        res = self.app.get(url, user=self.superuser)
        res = res.click("History")
        assert "Added permissions" in res.content.decode()
        assert "Removed permissions" in res.content.decode()
