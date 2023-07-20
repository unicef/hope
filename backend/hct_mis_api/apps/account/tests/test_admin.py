import json
from urllib.parse import unquote

from django.urls import reverse

from django_webtest import WebTest

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import User


class RoleTest(WebTest):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)

    def test_role_perm_matrix(self) -> None:
        url = reverse("admin:account_role_matrix")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200

    def test_role_sync(self) -> None:
        url = reverse("admin:account_role_dumpdata_qs")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200
        jres = json.loads(unquote(res.json["data"]))
        models = set([item["model"] for item in jres])
        assert len(models) == 1
        assert models == {"account.role"}
