from django.urls import reverse

from django_webtest import WebTest

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import User


class RoleTest(WebTest):
    def setUp(self):
        self.superuser: User = UserFactory(is_superuser=True, is_staff=True)

    def test_role_perm_patrix(self):
        url = reverse("admin:account_role_matrix")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200
