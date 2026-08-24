import json

import pytest
from requests.exceptions import ReadTimeout
import responses

from hope.apps.registration_data.api.country_workspace import CountryWorkspaceAPI

CALLBACK_URL = "https://cw.example.com/api/rdi/reset-callback/abc123"
SIGNED_TOKEN = "signed-token-abc123"


@responses.activate
def test_notify_posts_signed_token_in_body() -> None:
    responses.add(responses.POST, CALLBACK_URL, status=200)

    CountryWorkspaceAPI(api_url=CALLBACK_URL).notify_rdi_deleted(SIGNED_TOKEN)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == CALLBACK_URL
    assert json.loads(responses.calls[0].request.body) == {"signed_token": SIGNED_TOKEN}


@responses.activate
def test_notify_raises_on_non_2xx() -> None:
    responses.add(responses.POST, CALLBACK_URL, body=b"fail", status=500)

    with pytest.raises(CountryWorkspaceAPI.CountryWorkspaceAPIError):
        CountryWorkspaceAPI(api_url=CALLBACK_URL).notify_rdi_deleted(SIGNED_TOKEN)


@responses.activate
def test_notify_sends_no_auth_header() -> None:
    responses.add(responses.POST, CALLBACK_URL, status=200)

    CountryWorkspaceAPI(api_url=CALLBACK_URL).notify_rdi_deleted(SIGNED_TOKEN)

    assert "Authorization" not in responses.calls[0].request.headers


@responses.activate
def test_notify_reads_no_body() -> None:
    responses.add(responses.POST, CALLBACK_URL, status=200)

    CountryWorkspaceAPI(api_url=CALLBACK_URL).notify_rdi_deleted(SIGNED_TOKEN)

    assert len(responses.calls) == 1


@responses.activate
def test_notify_sends_explicit_timeout() -> None:
    responses.add(responses.POST, CALLBACK_URL, status=200)

    CountryWorkspaceAPI(api_url=CALLBACK_URL).notify_rdi_deleted(SIGNED_TOKEN)

    assert responses.calls[0].request.req_kwargs["timeout"] == (5, 30)


@responses.activate
def test_notify_propagates_read_timeout() -> None:
    responses.add(responses.POST, CALLBACK_URL, body=ReadTimeout("read timed out"))

    with pytest.raises(ReadTimeout):
        CountryWorkspaceAPI(api_url=CALLBACK_URL).notify_rdi_deleted(SIGNED_TOKEN)
