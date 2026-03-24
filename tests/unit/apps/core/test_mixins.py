import os
from typing import Type
from unittest.mock import MagicMock, patch

import pytest
from requests import Response, Session

from hope.apps.core.api.mixins import BaseAPI


@pytest.fixture
def api_class() -> Type[BaseAPI]:
    class TestAPI(BaseAPI):
        API_KEY_ENV_NAME = "TEST_API_KEY"
        API_URL_ENV_NAME = "TEST_API_URL"

    return TestAPI


@pytest.fixture
def api_instance(api_class: Type[BaseAPI]) -> BaseAPI:
    with patch.dict(
        os.environ,
        {"TEST_API_KEY": "test_fake_key", "TEST_API_URL": "http://test-hope.com"},
    ):
        return api_class()


def test_base_api_init_missing_credentials_raises_error(api_class):
    with patch.dict(os.environ, {"TEST_API_KEY": "", "TEST_API_URL": ""}):
        with pytest.raises(BaseAPI.APIMissingCredentialsError) as exc:
            api_class()

    assert "Missing TestAPI Key/URL" in str(exc.value)


def test_base_api_init_success_sets_credentials(api_instance):
    assert api_instance.api_key == "test_fake_key"
    assert api_instance.api_url == "http://test-hope.com"
    assert isinstance(api_instance._client, Session)
    assert api_instance._client.headers["Authorization"] == "Token test_fake_key"


def test_base_api_validate_response_success_returns_response(api_instance):
    mock_response = MagicMock(spec=Response)
    mock_response.ok = True

    result = api_instance.validate_response(mock_response)

    assert result == mock_response


def test_base_api_validate_response_failure_raises_error(api_instance):
    mock_response = MagicMock(spec=Response)
    mock_response.ok = False
    mock_response.content = b"Error"
    mock_response.url = "http://test-hope.com"

    with pytest.raises(BaseAPI.APIError) as exc:
        api_instance.validate_response(mock_response)

    assert "Invalid response" in str(exc.value)


@patch.object(Session, "post")
def test_base_api_post_success_returns_json(mock_post, api_instance):
    mock_response = MagicMock(spec=Response)
    mock_response.ok = True
    mock_response.json.return_value = {"key": "value"}
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    result, status_code = api_instance._post("/test-endpoint", data={"key": "value"})

    assert status_code == 200
    assert result == {"key": "value"}
    mock_post.assert_called_once_with("/test-endpoint", json={"key": "value"})


@patch.object(Session, "post")
def test_base_api_post_invalid_json_returns_empty_dict(mock_post, api_instance):
    mock_response = MagicMock(spec=Response)
    mock_response.ok = True
    mock_response.json.side_effect = ValueError
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    result, status_code = api_instance._post("/test-endpoint", data={"key": "value"})

    assert status_code == 200
    assert result == {}
    mock_post.assert_called_once_with("/test-endpoint", json={"key": "value"})


@patch.object(Session, "get")
def test_base_api_get_success_returns_json(mock_get, api_instance):
    mock_response = MagicMock(spec=Response)
    mock_response.ok = True
    mock_response.json.return_value = {"key": "value"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result, status_code = api_instance._get("/test-endpoint", params={"param": "value"})

    assert status_code == 200
    assert result == {"key": "value"}
    mock_get.assert_called_once_with("/test-endpoint", params={"param": "value"})


@patch.object(Session, "delete")
def test_base_api_delete_success_returns_json(mock_delete, api_instance):
    mock_response = MagicMock(spec=Response)
    mock_response.ok = True
    mock_response.json.return_value = {"key": "value"}
    mock_response.status_code = 200
    mock_delete.return_value = mock_response

    result, status_code = api_instance._delete("/test-endpoint", params={"param": "value"})

    assert status_code == 200
    assert result == {"key": "value"}
    mock_delete.assert_called_once_with("/test-endpoint", params={"param": "value"})


@patch.object(Session, "delete")
def test_base_api_delete_invalid_json_returns_empty_dict(mock_delete, api_instance):
    mock_response = MagicMock(spec=Response)
    mock_response.ok = True
    mock_response.json.side_effect = ValueError
    mock_response.status_code = 200
    mock_delete.return_value = mock_response

    result, status_code = api_instance._delete("/test-endpoint", params={"param": "value"})

    assert status_code == 200
    assert result == {}
    mock_delete.assert_called_once_with("/test-endpoint", params={"param": "value"})
