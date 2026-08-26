from unittest.mock import MagicMock, patch

from django.urls import reverse
import pytest

from extras.test_utils.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_user():
    user = UserFactory(
        username="root",
        email="root@root.com",
        is_staff=True,
        is_superuser=True,
        is_active=True,
        status="ACTIVE",
    )
    user.set_password("password")
    user.save()
    return user


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user, backend="django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def fetch_payload():
    return {
        "username": "aurora-user",
        "password": "aurora-password",
        "registration": 2,
        "start": 10,
        "end": 20,
    }


@patch("hope.admin.record.requests.get")
def test_fetch_builds_url_from_host_without_trailing_slash(
    mock_get: MagicMock, admin_client, fetch_payload: dict
) -> None:
    mock_get.return_value.__enter__.return_value = MagicMock(status_code=200, json=lambda: {"data": []})

    admin_client.post(
        reverse("admin:aurora_record_fetch"),
        {"host": "https://aurora.example.org", **fetch_payload},
    )

    mock_get.assert_called_once()
    assert mock_get.call_args[0][0] == "https://aurora.example.org/api/data/2/10/20/"


@patch("hope.admin.record.requests.get")
def test_fetch_builds_url_from_host_with_trailing_slash(mock_get: MagicMock, admin_client, fetch_payload: dict) -> None:
    mock_get.return_value.__enter__.return_value = MagicMock(status_code=200, json=lambda: {"data": []})

    admin_client.post(
        reverse("admin:aurora_record_fetch"),
        {"host": "https://aurora.example.org/", **fetch_payload},
    )

    mock_get.assert_called_once()
    assert mock_get.call_args[0][0] == "https://aurora.example.org/api/data/2/10/20/"
