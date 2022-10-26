import sys
from typing import Any, Callable

from django.http import HttpRequest

from sentry_sdk import configure_scope


class SentryScopeMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        super().__init__()

    # Note: must be listed AFTER AuthenticationMiddleware
    def __call__(self, request: HttpRequest) -> Any:
        sys.stderr.isatty = lambda: False
        with configure_scope() as scope:
            scope.set_tag("username", request.user.username)
            scope.set_tag("business_area", request.headers.get("Business-Area"))
            response = self.get_response(request)
        return response
