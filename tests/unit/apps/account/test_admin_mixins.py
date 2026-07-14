from types import SimpleNamespace
from unittest.mock import Mock

from constance.test import override_config
import pytest

from extras.test_utils.factories import UserFactory
from hope.admin.account_mixins import DjAdminManager, get_valid_kobo_username


def test_get_valid_kobo_username_sanitizes_special_characters() -> None:
    user = UserFactory.build(username="John.Doe+test@Example.com")

    assert get_valid_kobo_username(user) == "john_doe_test_at_example_com"


def test_init_builds_admin_and_login_urls() -> None:
    manager = DjAdminManager(kf_host="https://kobo.example.org")

    assert manager.admin_url == "https://kobo.example.org/admin/"
    assert manager.login_url == "https://kobo.example.org/admin/login/"
    assert manager.form_errors == []


def test_extract_errors_collects_errorlist_items() -> None:
    manager = DjAdminManager(kf_host="https://kobo.example.org")
    response = Mock(content=b'<ul class="errorlist"><li>Bad value</li></ul>')

    assert manager.extract_errors(response) == ["Bad value"]
    assert manager.form_errors == ["Bad value"]


def test_assert_response_passes_for_expected_status() -> None:
    manager = DjAdminManager(kf_host="https://kobo.example.org")
    manager._last_response = Mock(status_code=200, headers={})

    manager.assert_response(200)


def test_assert_response_raises_for_unexpected_status() -> None:
    manager = DjAdminManager(kf_host="https://kobo.example.org")
    manager._last_response = Mock(status_code=500, headers={})

    with pytest.raises(DjAdminManager.ResponseError, match="Unexpected code:500"):
        manager.assert_response([200, 302])


def test_assert_response_raises_on_unexpected_redirect_location() -> None:
    manager = DjAdminManager(kf_host="https://kobo.example.org")
    manager._last_response = Mock(status_code=302, headers={"location": "/somewhere/"})

    with pytest.raises(DjAdminManager.ResponseError, match="Unexpected redirect"):
        manager.assert_response(302, location="/expected/")


def test_client_is_cached_session_with_referer_header() -> None:
    manager = DjAdminManager(kf_host="https://kobo.example.org")

    client = manager.client

    assert client.headers["Referer"] == "https://kobo.example.org/admin/"
    assert manager.client is client


def test_logout_clears_credentials_in_session() -> None:
    manager = DjAdminManager(kf_host="https://kobo.example.org")
    request = SimpleNamespace(session={"kobo_username": "u", "kobo_password": "p"})

    manager.logout(request)

    assert request.session["kobo_username"] is None
    assert request.session["kobo_password"] is None


@override_config(KOBO_ADMIN_CREDENTIALS="missing-colon")
def test_login_raises_when_credentials_are_malformed() -> None:
    manager = DjAdminManager(kf_host="https://kobo.example.org")

    with pytest.raises(ValueError, match="Invalid KOBO_ADMIN_CREDENTIALS"):
        manager.login()


def test_get_csrfmiddlewaretoken_extracts_token() -> None:
    manager = DjAdminManager(kf_host="https://kobo.example.org")
    manager._last_response = Mock(content=b'<input name="csrfmiddlewaretoken" value="the-token">')

    assert manager.get_csrfmiddlewaretoken() == "the-token"


def test_get_csrfmiddlewaretoken_raises_when_token_missing() -> None:
    manager = DjAdminManager(kf_host="https://kobo.example.org")
    manager._last_response = Mock(content=b"<form></form>")

    with pytest.raises(ValueError, match="Unable to get CSRF token from Kobo"):
        manager.get_csrfmiddlewaretoken()
