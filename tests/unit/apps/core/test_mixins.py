import os
from typing import Type
from unittest.mock import MagicMock, patch

import pytest
from requests import Response, Session

from hope.apps.core.api.mixins import BaseAPI


@pytest.mark.django_db
class TestMixinBaseAPI:
    @pytest.fixture
    def api_class(self) -> Type[BaseAPI]:
        class TestAPI(BaseAPI):
            API_KEY_ENV_NAME = "TEST_API_KEY"
            API_URL_ENV_NAME = "TEST_API_URL"

        return TestAPI

    @pytest.fixture
    def api_instance(self, api_class: Type[BaseAPI]) -> BaseAPI:
        with patch.dict(
            os.environ,
            {"TEST_API_KEY": "test_fake_key", "TEST_API_URL": "http://test-hope.com"},
        ):
            return api_class()

    def test_init_missing_credentials(self, api_class: Type[BaseAPI]) -> None:
        with patch.dict(os.environ, {"TEST_API_KEY": "", "TEST_API_URL": ""}):
            with pytest.raises(BaseAPI.APIMissingCredentialsError) as exc:
                api_class()
            assert "Missing TestAPI Key/URL" in str(exc.value)

    def test_init_success(self, api_instance: BaseAPI) -> None:
        assert api_instance.api_key == "test_fake_key"
        assert api_instance.api_url == "http://test-hope.com"
        assert isinstance(api_instance._client, Session)
        assert api_instance._client.headers["Authorization"] == "Token test_fake_key"

    def test_validate_response_success(self, api_instance: BaseAPI) -> None:
        mock_response = MagicMock(spec=Response)
        mock_response.ok = True
        assert api_instance.validate_response(mock_response) == mock_response

    def test_validate_response_failure(self, api_instance: BaseAPI) -> None:
        mock_response = MagicMock(spec=Response)
        mock_response.ok = False
        mock_response.content = b"Error"
        mock_response.url = "http://test-hope.com"
        with pytest.raises(BaseAPI.APIError) as exc:
            api_instance.validate_response(mock_response)
        assert "Invalid response" in str(exc.value)

    @patch.object(Session, "post")
    def test_post_success(self, mock_post: MagicMock, api_instance: BaseAPI) -> None:
        mock_response = MagicMock(spec=Response)
        mock_response.ok = True
        mock_response.json.return_value = {"key": "value"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result, status_code = api_instance._post("/test-endpoint", data={"key": "value"})
        assert status_code == 200
        assert result == {"key": "value"}
        mock_post.assert_called_once_with("http://test-hope.com/test-endpoint", json={"key": "value"})

    @patch.object(Session, "post")
    def test_post_invalid_json(self, mock_post: MagicMock, api_instance: BaseAPI) -> None:
        mock_response = MagicMock(spec=Response)
        mock_response.ok = True
        mock_response.json.side_effect = ValueError
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result, status_code = api_instance._post("/test-endpoint", data={"key": "value"})
        assert status_code == 200
        assert result == {}
        mock_post.assert_called_once_with("http://test-hope.com/test-endpoint", json={"key": "value"})

    @patch.object(Session, "get")
    def test_get_success(self, mock_get: MagicMock, api_instance: BaseAPI) -> None:
        mock_response = MagicMock(spec=Response)
        mock_response.ok = True
        mock_response.json.return_value = {"key": "value"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result, status_code = api_instance._get("/test-endpoint", params={"param": "value"})
        assert status_code == 200
        assert result == {"key": "value"}
        mock_get.assert_called_once_with("http://test-hope.com/test-endpoint", params={"param": "value"})

    @patch.object(Session, "delete")
    def test_delete_success(self, mock_delete: MagicMock, api_instance: BaseAPI) -> None:
        mock_response = MagicMock(spec=Response)
        mock_response.ok = True
        mock_response.json.return_value = {"key": "value"}
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        result, status_code = api_instance._delete("/test-endpoint", params={"param": "value"})
        assert status_code == 200
        assert result == {"key": "value"}
        mock_delete.assert_called_once_with("http://test-hope.com/test-endpoint", params={"param": "value"})

    @patch.object(Session, "delete")
    def test_delete_invalid_json(self, mock_delete: MagicMock, api_instance: BaseAPI) -> None:
        mock_response = MagicMock(spec=Response)
        mock_response.ok = True
        mock_response.json.side_effect = ValueError
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        result, status_code = api_instance._delete("/test-endpoint", params={"param": "value"})
        assert status_code == 200
        assert result == {}
        mock_delete.assert_called_once_with("http://test-hope.com/test-endpoint", params={"param": "value"})
