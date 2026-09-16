from dataclasses import dataclass, field
from typing import Any

from django.test import override_settings
import pytest
from rest_framework import status
from rest_framework.response import Response

from hope.api.caches import etag_decorator

ETAG_VALUE = "etag_value"


class DummyKeyConstructor:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> str:
        return ETAG_VALUE


@dataclass
class DummyRequest:
    method: str = "GET"
    headers: dict = field(default_factory=dict)


class DummyView:
    @etag_decorator(DummyKeyConstructor)
    def default_view(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """A dummy view docstring."""
        return Response()

    @etag_decorator(DummyKeyConstructor, compare_etags=False)
    def no_compare_view(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        return Response()

    @etag_decorator(DummyKeyConstructor, safe_only=False)
    def unsafe_view(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        return Response()


@pytest.fixture
def view() -> DummyView:
    return DummyView()


def test_wraps_preserves_name() -> None:
    assert DummyView.default_view.__name__ == "default_view"


def test_wraps_preserves_docstring() -> None:
    assert DummyView.default_view.__doc__ == "A dummy view docstring."


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_unsafe_method_bypasses_etag_logic(view: DummyView, method: str) -> None:
    request = DummyRequest(method=method, headers={"If-None-Match": ETAG_VALUE})
    response = view.default_view(request)

    assert response.status_code == status.HTTP_200_OK
    assert "ETag" not in response.headers


def test_head_applies_etag_logic(view: DummyView) -> None:
    request = DummyRequest(method="HEAD", headers={"If-None-Match": ETAG_VALUE})
    response = view.default_view(request)

    assert response.status_code == status.HTTP_304_NOT_MODIFIED


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_safe_only_false_applies_etag_to_unsafe_methods(view: DummyView, method: str) -> None:
    request = DummyRequest(method=method, headers={"If-None-Match": ETAG_VALUE})
    response = view.unsafe_view(request)

    assert response.status_code == status.HTTP_304_NOT_MODIFIED
    assert response.headers["ETag"] == ETAG_VALUE


def test_matching_etag_returns_304(view: DummyView) -> None:
    request = DummyRequest(headers={"If-None-Match": ETAG_VALUE})
    response = view.default_view(request)

    assert response.status_code == status.HTTP_304_NOT_MODIFIED
    assert response.headers["ETag"] == ETAG_VALUE


def test_no_header_returns_200(view: DummyView) -> None:
    response = view.default_view(DummyRequest())

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["ETag"] == ETAG_VALUE


def test_stale_etag_returns_200(view: DummyView) -> None:
    request = DummyRequest(headers={"If-None-Match": "stale"})
    response = view.default_view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["ETag"] == ETAG_VALUE


def test_compare_etags_false_returns_200(view: DummyView) -> None:
    request = DummyRequest(headers={"If-None-Match": ETAG_VALUE})
    response = view.no_compare_view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["ETag"] == ETAG_VALUE


@override_settings(DEBUG=True)
def test_debug_mode_returns_200(view: DummyView) -> None:
    request = DummyRequest(headers={"If-None-Match": ETAG_VALUE})
    response = view.default_view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["ETag"] == ETAG_VALUE


def test_200_response_headers(view: DummyView) -> None:
    response = view.default_view(DummyRequest())

    assert response.headers["ETag"] == ETAG_VALUE
    assert response.headers["Cache-Control"] == "private, no-cache"
    assert response.headers["Vary"] == "Authorization, Cookie"


def test_304_response_headers(view: DummyView) -> None:
    request = DummyRequest(headers={"If-None-Match": ETAG_VALUE})
    response = view.default_view(request)

    assert response.headers["ETag"] == ETAG_VALUE
    assert response.headers["Cache-Control"] == "private, no-cache"
    assert response.headers["Vary"] == "Authorization, Cookie"
