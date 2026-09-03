from unittest.mock import MagicMock, patch

from hope.middlewares.version import VersionMiddleware


@patch("hope.middlewares.version.settings")
def test_version_middleware_sets_header(mocked_settings: MagicMock) -> None:
    mocked_settings.VERSION = "1.2.3"
    response_sentinel = MagicMock()
    get_response = MagicMock(return_value=response_sentinel)
    middleware = VersionMiddleware(get_response)
    request = MagicMock()

    result = middleware(request)

    assert result is response_sentinel
    get_response.assert_called_once_with(request)
    assert response_sentinel.__setitem__.call_args[0] == ("X-Hope-Backend-Version", "1.2.3")


@patch("hope.middlewares.version.settings")
def test_version_middleware_handles_none_version(mocked_settings: MagicMock) -> None:
    mocked_settings.VERSION = None
    response_sentinel = MagicMock()
    get_response = MagicMock(return_value=response_sentinel)
    middleware = VersionMiddleware(get_response)
    request = MagicMock()

    result = middleware(request)

    assert result is response_sentinel
    assert response_sentinel.__setitem__.call_args[0] == ("X-Hope-Backend-Version", "")
