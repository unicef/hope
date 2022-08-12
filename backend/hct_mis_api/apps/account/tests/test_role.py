from django.urls import reverse

from django_webtest import WebTest

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import Role, User


class RoleTest(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.role_1 = Role.objects.create(name="Role_1")
        cls.user = UserFactory()
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)

    def test_role_history(self):
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

    def test_role_matrix(self):
        url = reverse("admin:account_role_changelist")
        res = self.app.get(url, user=self.superuser)
        res = res.click("Matrix")
