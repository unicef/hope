from django.http import HttpRequest, HttpResponse

from hope.middlewares.version import VersionMiddleware


def test_call_sets_version_header_when_version_configured(settings: object) -> None:
    settings.VERSION = "1.2.3"

    middleware = VersionMiddleware(lambda request: HttpResponse("ok"))
    response = middleware(HttpRequest())

    assert response["X-Hope-Backend-Version"] == "1.2.3"


def test_call_when_get_response_returns_none_and_no_version(
    settings: object,
) -> None:
    settings.VERSION = ""

    middleware = VersionMiddleware(lambda request: None)
    response = middleware(HttpRequest())

    assert response is None
