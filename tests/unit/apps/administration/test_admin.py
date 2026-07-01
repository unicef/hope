from typing import TYPE_CHECKING, Any, Callable
from unittest.mock import MagicMock, patch

from django.contrib.admin import ModelAdmin, site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse
import pytest

from extras.test_utils.factories import BusinessAreaFactory, UserFactory
from hope.apps.account.permissions import Permissions

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp

    from hope.models import BusinessArea, User

pytestmark = pytest.mark.django_db


EXCLUDED_MODELS: list[str] = []


def get_model_admins():
    """Get all registered admin models for parametrization."""
    return [
        pytest.param(model.__name__, admin, id=model.__name__)
        for model, admin in site._registry.items()
        if model.__name__ not in EXCLUDED_MODELS
    ]


@pytest.fixture
def superuser(db: Any) -> "User":
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture
def business_area(db: Any) -> "BusinessArea":
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        slug="afghanistan",
        active=True,
    )


def test_elasticsearch_panel_info_action(
    django_app: "DjangoTestApp",
    superuser: "User",
) -> None:
    url = reverse("admin:console-es")
    mock_conn = MagicMock()
    mock_conn.info.return_value.body = {"cluster_name": "test-cluster", "version": {"number": "9.0.1"}}
    with patch("hope.apps.administration.panels.es.create_connection", return_value=mock_conn):
        get_response = django_app.get(url, user=superuser)
        form = next(f for f in get_response.forms.values() if "action" in f.fields)
        form["action"] = "info"
        response = form.submit()
    assert response.status_code == 200
    mock_conn.info.assert_called_once()


@pytest.mark.parametrize(("name", "model_admin"), get_model_admins())
def test_admin_changelist_returns_200_for_superuser(
    django_app: "DjangoTestApp",
    superuser: "User",
    business_area: "BusinessArea",
    create_user_role_with_permissions: Callable,
    name: str,
    model_admin: ModelAdmin,
) -> None:
    create_user_role_with_permissions(
        superuser,
        [Permissions.DOWNLOAD_STORAGE_FILE],
        business_area,
        whole_business_area_access=True,
    )
    url = reverse(admin_urlname(model_admin.model._meta, "changelist"))
    res = django_app.get(url, user=superuser)
    if res.status_code == 302:
        res = res.follow()
    assert res.status_code == 200
