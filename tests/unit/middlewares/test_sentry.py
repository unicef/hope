from unittest.mock import MagicMock, patch

from hope.middlewares.sentry import SentryScopeMiddleware, is_country_name


def test_is_country_name_returns_true_for_known_country() -> None:
    assert is_country_name("Ukraine") is True


def test_is_country_name_returns_false_for_unknown_country() -> None:
    assert is_country_name("Test123") is False


@patch("hope.middlewares.sentry.sentry_sdk")
def test_call_uses_business_area_header_when_present(mocked_sentry: MagicMock) -> None:
    scope = MagicMock()
    mocked_sentry.get_isolation_scope.return_value = scope
    response_sentinel = object()
    get_response = MagicMock(return_value=response_sentinel)
    middleware = SentryScopeMiddleware(get_response)
    request = MagicMock()
    request.headers = {"Business-Area": "ukraine"}
    request.path = "/api/rest/afghanistan/rdi/upload/"
    request.user.username = "alice"

    result = middleware(request)

    assert result is response_sentinel
    get_response.assert_called_once_with(request)
    scope.set_tag.assert_any_call("username", "alice")
    scope.set_tag.assert_any_call("business_area", "ukraine")


@patch("hope.middlewares.sentry.sentry_sdk")
def test_call_derives_business_area_from_api_rest_path_when_header_missing(
    mocked_sentry: MagicMock,
) -> None:
    scope = MagicMock()
    mocked_sentry.get_isolation_scope.return_value = scope
    get_response = MagicMock()
    middleware = SentryScopeMiddleware(get_response)
    request = MagicMock()
    request.headers = {}
    request.path = "/api/rest/ukraine/rdi/upload/"
    request.user.username = "bob"

    middleware(request)

    scope.set_tag.assert_any_call("username", "bob")
    scope.set_tag.assert_any_call("business_area", "ukraine")


@patch("hope.middlewares.sentry.sentry_sdk")
def test_call_falls_back_to_default_business_area_when_path_does_not_match(
    mocked_sentry: MagicMock,
) -> None:
    scope = MagicMock()
    mocked_sentry.get_isolation_scope.return_value = scope
    get_response = MagicMock()
    middleware = SentryScopeMiddleware(get_response)
    request = MagicMock()
    request.headers = {}
    request.path = "/api/admin/account/role/"
    request.user.username = "carol"

    middleware(request)

    scope.set_tag.assert_any_call("username", "carol")
    scope.set_tag.assert_any_call("business_area", "NO_BA")
