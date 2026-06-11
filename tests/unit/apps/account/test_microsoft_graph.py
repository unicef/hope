from django.conf import settings
from django.http import Http404
from django.test import override_settings
import pytest
import requests
import responses

from hope.apps.account.microsoft_graph import MicrosoftGraphAPI


@override_settings(AZURE_CLIENT_ID="", AZURE_CLIENT_SECRET="")
def test_get_token_raises_when_credentials_missing() -> None:
    with pytest.raises(ValueError, match="Configure AZURE_CLIENT_ID and/or AZURE_CLIENT_SECRET"):
        MicrosoftGraphAPI()


@override_settings(AZURE_CLIENT_ID="client-id", AZURE_CLIENT_SECRET="client-secret")
@responses.activate
def test_get_token_returns_access_token() -> None:
    responses.add(responses.POST, settings.AZURE_TOKEN_URL, json={"access_token": "the-token"}, status=200)

    api = MicrosoftGraphAPI()

    assert api.access_token == "the-token"


@override_settings(AZURE_CLIENT_ID="client-id", AZURE_CLIENT_SECRET="client-secret")
@responses.activate
def test_get_token_raises_when_azure_returns_non_200() -> None:
    responses.add(responses.POST, settings.AZURE_TOKEN_URL, body=b"fail", status=500)

    with pytest.raises(Exception, match="Unable to fetch token from Azure. 500 fail"):
        MicrosoftGraphAPI()


@override_settings(AZURE_CLIENT_ID="client-id", AZURE_CLIENT_SECRET="client-secret")
@responses.activate
def test_get_results_returns_json() -> None:
    responses.add(responses.POST, settings.AZURE_TOKEN_URL, json={"access_token": "the-token"}, status=200)
    responses.add(responses.GET, "https://graph.microsoft.com/v1.0/me", json={"id": "abc"}, status=200)
    api = MicrosoftGraphAPI()

    result = api.get_results("https://graph.microsoft.com/v1.0/me")

    assert result == {"id": "abc"}


@override_settings(AZURE_CLIENT_ID="client-id", AZURE_CLIENT_SECRET="client-secret")
@responses.activate
def test_get_results_raises_on_http_error() -> None:
    responses.add(responses.POST, settings.AZURE_TOKEN_URL, json={"access_token": "the-token"}, status=200)
    responses.add(responses.GET, "https://graph.microsoft.com/v1.0/me", json={"error": "nope"}, status=404)
    api = MicrosoftGraphAPI()

    with pytest.raises(requests.exceptions.HTTPError):
        api.get_results("https://graph.microsoft.com/v1.0/me")


@override_settings(AZURE_CLIENT_ID="client-id", AZURE_CLIENT_SECRET="client-secret")
@responses.activate
def test_get_user_data_by_uuid_returns_user() -> None:
    responses.add(responses.POST, settings.AZURE_TOKEN_URL, json={"access_token": "the-token"}, status=200)
    responses.add(
        responses.GET,
        "https://graph.microsoft.com/v1.0/users/uuid-123",
        json={"id": "uuid-123", "mail": "user@example.com"},
        status=200,
    )
    api = MicrosoftGraphAPI()

    result = api.get_user_data(uuid="uuid-123")

    assert result == {"id": "uuid-123", "mail": "user@example.com"}


@override_settings(AZURE_CLIENT_ID="client-id", AZURE_CLIENT_SECRET="client-secret")
@responses.activate
def test_get_user_data_by_email_returns_first_match() -> None:
    responses.add(responses.POST, settings.AZURE_TOKEN_URL, json={"access_token": "the-token"}, status=200)
    responses.add(
        responses.GET,
        "https://graph.microsoft.com/v1.0/users/",
        json={"value": [{"id": "1", "mail": "user@example.com"}]},
        status=200,
    )
    api = MicrosoftGraphAPI()

    result = api.get_user_data(email="user@example.com")

    assert result == {"id": "1", "mail": "user@example.com"}


@override_settings(AZURE_CLIENT_ID="client-id", AZURE_CLIENT_SECRET="client-secret")
@responses.activate
def test_get_user_data_without_email_or_uuid_raises_value_error() -> None:
    responses.add(responses.POST, settings.AZURE_TOKEN_URL, json={"access_token": "the-token"}, status=200)
    api = MicrosoftGraphAPI()

    with pytest.raises(ValueError, match="You must provide 'uuid' or 'email' argument."):
        api.get_user_data()


@override_settings(AZURE_CLIENT_ID="client-id", AZURE_CLIENT_SECRET="client-secret")
@responses.activate
def test_get_user_data_by_email_raises_http404_when_no_match() -> None:
    responses.add(responses.POST, settings.AZURE_TOKEN_URL, json={"access_token": "the-token"}, status=200)
    responses.add(responses.GET, "https://graph.microsoft.com/v1.0/users/", json={"value": []}, status=200)
    api = MicrosoftGraphAPI()

    with pytest.raises(Http404, match="User not found"):
        api.get_user_data(email="missing@example.com")


@override_settings(AZURE_CLIENT_ID="client-id", AZURE_CLIENT_SECRET="client-secret")
@responses.activate
def test_get_user_data_by_uuid_raises_http404_when_empty() -> None:
    responses.add(responses.POST, settings.AZURE_TOKEN_URL, json={"access_token": "the-token"}, status=200)
    responses.add(responses.GET, "https://graph.microsoft.com/v1.0/users/uuid-123", json={}, status=200)
    api = MicrosoftGraphAPI()

    with pytest.raises(Http404, match="User not found"):
        api.get_user_data(uuid="uuid-123")
