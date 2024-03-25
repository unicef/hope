import sys
from typing import Any, Callable

from django.http import HttpRequest

import pycountry
from sentry_sdk import configure_scope


class SentryScopeMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        super().__init__()

    # Note: must be listed AFTER AuthenticationMiddleware
    def __call__(self, request: HttpRequest) -> Any:
        sys.stderr.isatty = lambda: False  # type: ignore # I guess this is a hack to make Sentry not use colors in the terminal?
        with configure_scope() as scope:
            business_area = request.headers.get("Business-Area")
            if not business_area:
                business_area = "NO_BA"
                country_from_path = request.path.split("/")
                country_name = country_from_path[3] if len(country_from_path) > 3 else None
                if country_name:
                    business_area = country_name if pycountry.countries.lookup(country_name) else "NO_BA"
            scope.set_tag("username", request.user.username)
            scope.set_tag("business_area", business_area)
            response = self.get_response(request)
        return response
