import pytest
import responses

from hope.apps.registration_data.api.country_workspace import CountryWorkspaceAPI

CALLBACK_URL = "https://cw.example.com/api/rdi/reset-callback/abc123"


@responses.activate
def test_notify_posts_to_callback_url_no_body() -> None:
    responses.add(responses.POST, CALLBACK_URL, status=200)

    CountryWorkspaceAPI(api_url=CALLBACK_URL).notify_rdi_deleted()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == CALLBACK_URL
    assert responses.calls[0].request.body is None


@responses.activate
def test_notify_raises_on_non_2xx() -> None:
    responses.add(responses.POST, CALLBACK_URL, body=b"fail", status=500)

    with pytest.raises(CountryWorkspaceAPI.CountryWorkspaceAPIError):
        CountryWorkspaceAPI(api_url=CALLBACK_URL).notify_rdi_deleted()


@responses.activate
def test_notify_sends_no_auth_header() -> None:
    responses.add(responses.POST, CALLBACK_URL, status=200)

    CountryWorkspaceAPI(api_url=CALLBACK_URL).notify_rdi_deleted()

    assert "Authorization" not in responses.calls[0].request.headers


@responses.activate
def test_notify_reads_no_body() -> None:
    responses.add(responses.POST, CALLBACK_URL, status=200)

    CountryWorkspaceAPI(api_url=CALLBACK_URL).notify_rdi_deleted()

    assert len(responses.calls) == 1
