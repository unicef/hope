from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse


class VersionMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        super().__init__()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response["X-Hope-Backend-Version"] = settings.VERSION or ""
        return response
