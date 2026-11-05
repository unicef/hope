"""social-auth-app-django 6 accepts login only as a CSRF-protected POST."""

from typing import Any
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from django.test import Client
from django.urls import reverse
import pytest
from social_core.backends.azuread_tenant import AzureADTenantOAuth2
from social_django.models import Nonce

from extras.test_utils.factories import UserFactory
from hope.models import User

pytestmark = pytest.mark.django_db

BEGIN_URL = "/api/login/azuread-tenant-oauth2/"
COMPLETE_URL = "/api/complete/azuread-tenant-oauth2/"


@pytest.fixture
def csrf_client() -> Client:
    return Client(enforce_csrf_checks=True)


@pytest.fixture
def csrf_token(csrf_client: Client) -> str:
    return csrf_client.get(reverse("csrf-token")).json()["csrf_token"]


@pytest.fixture
def user() -> User:
    return UserFactory(email="azure.user@example.com")


@pytest.fixture
def azure_client_secret(settings: Any) -> None:
    settings.SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET = "secret"


def test_social_login_begin_rejects_get(csrf_client: Client) -> None:
    response = csrf_client.get(BEGIN_URL)

    assert response.status_code == 405


def test_social_login_begin_rejects_post_without_csrf_token(csrf_client: Client) -> None:
    response = csrf_client.post(BEGIN_URL)

    assert response.status_code == 403


def test_social_login_begin_redirects_to_azure_with_csrf_token_and_stores_next(
    csrf_client: Client, csrf_token: str
) -> None:
    response = csrf_client.post(BEGIN_URL, {"csrfmiddlewaretoken": csrf_token, "next": "/programs/"})

    assert response.status_code == 302
    assert urlparse(response.url).hostname == "login.microsoftonline.com"
    assert csrf_client.session["next"] == "/programs/"


# Only the two calls to Azure are mocked, so state validation and the nonce consumption run as in production.
def test_social_login_complete_logs_in_existing_user_and_consumes_state_nonce(
    csrf_client: Client, csrf_token: str, user: User, azure_client_secret: None
) -> None:
    begin = csrf_client.post(BEGIN_URL, {"csrfmiddlewaretoken": csrf_token})
    state = parse_qs(urlparse(begin.url).query)["state"][0]

    with (
        patch.object(
            AzureADTenantOAuth2, "request_access_token", return_value={"access_token": "at", "id_token": "it"}
        ),
        patch.object(AzureADTenantOAuth2, "user_data", return_value={"sub": "sub-1", "email": user.email}),
    ):
        response = csrf_client.get(COMPLETE_URL, {"code": "abc", "state": state})

    assert response.status_code == 302
    assert csrf_client.session["_auth_user_id"] == str(user.pk)
    assert not Nonce.objects.exists()


def test_login_required_view_redirects_anonymous_user_to_spa_login_page(client: Client) -> None:
    response = client.get("/api/changelog/")

    assert response.status_code == 302
    assert response.url == "/login?next=/api/changelog/"


def test_admin_login_page_posts_to_social_login_with_csrf_token(client: Client) -> None:
    response = client.get(reverse("admin:login"), {"next": "/api/unicorn/"})

    content = response.content.decode()
    assert f'<form method="post" action="{BEGIN_URL}">' in content
    assert 'name="csrfmiddlewaretoken"' in content
    assert '<input type="hidden" name="next" value="/api/unicorn/">' in content
