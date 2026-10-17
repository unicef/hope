"""social-auth-app-django 6 accepts login only as a CSRF-protected POST."""

from urllib.parse import urlparse

from django.test import Client
from django.urls import reverse
import pytest

pytestmark = pytest.mark.django_db

BEGIN_URL = "/api/login/azuread-tenant-oauth2/"


@pytest.fixture
def csrf_client() -> Client:
    return Client(enforce_csrf_checks=True)


@pytest.fixture
def csrf_token(csrf_client: Client) -> str:
    return csrf_client.get(reverse("csrf-token")).json()["csrf_token"]


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
