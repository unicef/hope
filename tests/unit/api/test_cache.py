from typing import Any

import pytest
from rest_framework import status
from rest_framework.response import Response

from hope.api.caches import etag_decorator

pytestmark = pytest.mark.django_db()


class TestEtagDecorator:
    class DummyEtagConstructorClass:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def __call__(self, *args: Any, **kwargs: Any) -> str:
            return "etag"

    class DummyRequest:
        def __init__(self, headers: dict) -> None:
            self.headers = headers

    @etag_decorator(DummyEtagConstructorClass)
    def dummy_view(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        return Response()

    def test_etag_decorator_etag_exists(self) -> None:
        response = self.dummy_view(self.DummyRequest({"If-None-Match": "etag"}), (1, 2, 3), {})
        assert response.status_code == status.HTTP_304_NOT_MODIFIED
        assert response.headers["ETAG"] == "etag"

    def test_etag_decorator_etag_not_exists(self) -> None:
        response = self.dummy_view(self.DummyRequest({}), (1, 2, 3), {})
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["ETAG"] == "etag"

    def test_etag_decorator_old_etag(self) -> None:
        response = self.dummy_view(self.DummyRequest({"If-None-Match": "old"}), (1, 2, 3), {})
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["ETAG"] == "etag"
