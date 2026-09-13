from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

from django.db.models import Max
from django.test import override_settings
import pytest
from rest_framework import status
from rest_framework.response import Response

from extras.test_utils.factories.core import BusinessAreaFactory
from hope.api.caches import BusinessAreaAndProgramLastUpdatedKeyBit, etag_decorator, get_or_create_cache_key
from hope.models import BusinessArea

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


@pytest.mark.django_db
def test_business_area_and_program_last_updated_key_bit_builds_key() -> None:
    slug = "keybit-test"
    BusinessAreaFactory(slug=slug)
    program_code = "TEST-PROGRAM"
    key_bit = BusinessAreaAndProgramLastUpdatedKeyBit()
    key_bit.specific_view_cache_key = "payment_plan_list"
    view = SimpleNamespace(get_queryset=BusinessArea.objects.all)

    key = key_bit.get_data(
        params=None,
        view_instance=view,
        view_method=None,
        request=None,
        args=(),
        kwargs={"business_area_slug": slug, "program_code": program_code},
    )

    version = get_or_create_cache_key(f"{slug}:version", 1)
    latest_updated_at = BusinessArea.objects.aggregate(latest_updated_at=Max("updated_at"))["latest_updated_at"]
    assert key == (
        f"{slug}:{version}:{program_code}:payment_plan_list:{latest_updated_at}:{BusinessArea.objects.all().count()}"
    )


@pytest.mark.django_db
def test_business_area_and_program_last_updated_key_bit_changes_when_queryset_mutates() -> None:
    slug = "keybit-test"
    BusinessAreaFactory(slug=slug)
    key_bit = BusinessAreaAndProgramLastUpdatedKeyBit()
    key_bit.specific_view_cache_key = "payment_plan_list"
    view = SimpleNamespace(get_queryset=BusinessArea.objects.all)
    kwargs = {"business_area_slug": slug, "program_code": "TEST-PROGRAM"}

    key_before = key_bit.get_data(None, view, None, None, (), kwargs)

    BusinessAreaFactory()

    key_after = key_bit.get_data(None, view, None, None, (), kwargs)
    assert key_after != key_before
