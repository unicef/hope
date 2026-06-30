from smtplib import SMTPException
from typing import Any

from django.conf import settings
from django.contrib.messages import get_messages
from django.core import mail
from django.test import Client
from django.urls import reverse
import pytest

from extras.test_utils.factories import UserFactory
from hope.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def superuser() -> User:
    return UserFactory(is_staff=True, is_superuser=True, email="admin@example.com")


@pytest.fixture
def superuser_client(client: Client, superuser: User) -> Client:
    client.force_login(superuser, "django.contrib.auth.backends.ModelBackend")
    return client


def test_email_panel_get_masks_password_for_non_root(superuser_client: Client) -> None:
    response = superuser_client.get(reverse("admin:console-email"))

    assert response.status_code == 200
    assert response.context["smtp"]["EMAIL_HOST_PASSWORD"] == "****"


def test_email_panel_get_reveals_password_for_root(superuser_client: Client) -> None:
    response = superuser_client.get(
        reverse("admin:console-email"),
        headers={"x-root-token": settings.ROOT_TOKEN},
    )

    assert response.status_code == 200
    assert response.context["smtp"]["EMAIL_HOST_PASSWORD"] == settings.EMAIL_HOST_PASSWORD


def test_email_panel_post_sends_email_and_reports_success(superuser_client: Client, superuser: User) -> None:
    response = superuser_client.post(reverse("admin:console-email"))

    assert response.status_code == 200
    assert mail.outbox[0].to == [superuser.email]
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert messages == [f"Email sent to {superuser.email}"]


def test_email_panel_post_no_success_message_when_send_returns_zero(superuser_client: Client, mocker: Any) -> None:
    mocker.patch("django.core.mail.send_mail", return_value=0)

    response = superuser_client.post(reverse("admin:console-email"))

    assert response.status_code == 200
    assert list(get_messages(response.wsgi_request)) == []


def test_email_panel_post_reports_thread_error_when_send_raises(superuser_client: Client, mocker: Any) -> None:
    mocker.patch(
        "django.core.mail.send_mail",
        side_effect=RuntimeError("err"),
    )

    response = superuser_client.post(reverse("admin:console-email"))

    assert response.status_code == 200
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert messages == ["RuntimeError: err"]


def test_email_panel_post_reports_smtp_exception(superuser_client: Client, mocker: Any) -> None:
    mocker.patch(
        "django.core.mail.get_connection",
        side_effect=SMTPException("no smtp"),
    )

    response = superuser_client.post(reverse("admin:console-email"))

    assert response.status_code == 200
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert messages == ["SMTPException: no smtp"]
