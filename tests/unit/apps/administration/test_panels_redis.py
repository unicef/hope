from django.test import Client
from django.urls import reverse
import pytest

from extras.test_utils.factories import UserFactory
from hope.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def staff_user() -> User:
    return UserFactory(is_staff=True)


@pytest.fixture
def superuser() -> User:
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture
def staff_client(client: Client, staff_user: User) -> Client:
    client.force_login(staff_user, "django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def superuser_client(client: Client, superuser: User) -> Client:
    client.force_login(superuser, "django.contrib.auth.backends.ModelBackend")
    return client


def test_redis_panel_returns_403_for_staff_without_superuser(staff_client: Client) -> None:
    response = staff_client.get(reverse("admin:console-panel_redis"))

    assert response.status_code == 403


def test_redis_panel_renders_command_form_for_superuser(superuser_client: Client) -> None:
    response = superuser_client.get(reverse("admin:console-panel_redis"))

    assert response.status_code == 200
    assert response.context["title"] == "Redis CLI"
