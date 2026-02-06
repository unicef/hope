from typing import TYPE_CHECKING, Any, Callable

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
    assert res.status_code == 200
