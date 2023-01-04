from django.urls import reverse

from django_webtest import WebTest

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import User


class RoleTest(WebTest):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)

    def test_role_perm_patrix(self) -> None:
        url = reverse("admin:account_role_matrix")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200
