from typing import Callable

from django.conf import settings
from django.http import HttpRequest


class VersionMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        super().__init__()

    def __call__(self, request: HttpRequest) -> object:
        response = self.get_response(request)
        response["X-Hope-Backend-Version"] = settings.VERSION
        return response
