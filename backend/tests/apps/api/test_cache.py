from rest_framework import status
from rest_framework.response import Response

from hct_mis_api.api.caches import etag_decorator


class TestEtagDecorator:
    class DummyEtagConstructorClass:
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            return "etag"

    class DummyRequest:
        def __init__(self, headers: dict):
            self.headers = headers

    @etag_decorator(DummyEtagConstructorClass)
    def dummy_view(self, request, *args, **kwargs):
        return Response()

    def test_etag_decorator_etag_exists(self):
        response = self.dummy_view(self.DummyRequest({"ETAG": "etag"}), (1, 2, 3), {})
        assert response.status_code == status.HTTP_304_NOT_MODIFIED
        assert response.headers["ETAG"] == "etag"

    def test_etag_decorator_etag_not_exists(self):
        response = self.dummy_view(self.DummyRequest({}), (1, 2, 3), {})
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["ETAG"] == "etag"

    def test_etag_decorator_old_etag(self):
        response = self.dummy_view(self.DummyRequest({"ETAG": "old"}), (1, 2, 3), {})
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["ETAG"] == "etag"
