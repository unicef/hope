import json
from urllib.parse import unquote

from django.urls import reverse

import pytest
from django_webtest import DjangoTestApp

from hct_mis_api.apps.account.fixtures import RoleFactory, UserFactory
from hct_mis_api.apps.account.models import Partner, Role, User


@pytest.fixture
def superuser(request: pytest.FixtureRequest, partner_unicef: Partner) -> User:
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture
def role(request: pytest.FixtureRequest) -> Role:
    return RoleFactory(name="Role")


def test_role_perm_matrix(django_app: DjangoTestApp, superuser: pytest.FixtureRequest) -> None:
    url = reverse("admin:account_role_matrix")
    res = django_app.get(url, user=superuser)
    assert res.status_code == 200


def test_role_sync(django_app: DjangoTestApp, superuser: User, role: Role) -> None:
    url = reverse("admin:account_role_dumpdata_qs")
    res = django_app.get(url, user=superuser)
    assert res.status_code == 200
    jres = json.loads(unquote(res.json["data"]))
    models = {item["model"] for item in jres}
    assert len(models) == 1
    assert models == {"account.role"}
