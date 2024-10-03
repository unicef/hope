import json
from urllib.parse import unquote

from django.urls import reverse

import pytest

from hct_mis_api.apps.account.fixtures import RoleFactory, UserFactory


@pytest.fixture()
def superuser(request, db):
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture()
def role(request, db):
    return RoleFactory(name="Role")


def test_role_perm_matrix(django_app, superuser) -> None:
    url = reverse("admin:account_role_matrix")
    res = django_app.get(url, user=superuser)
    assert res.status_code == 200


def test_role_sync(django_app, superuser, role) -> None:
    url = reverse("admin:account_role_dumpdata_qs")
    res = django_app.get(url, user=superuser)
    assert res.status_code == 200
    print(res.json)
    jres = json.loads(unquote(res.json["data"]))
    models = set([item["model"] for item in jres])
    assert len(models) == 1
    assert models == {"account.role"}
