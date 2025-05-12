import re
import sys
from typing import Any, Callable

from django.http import HttpRequest

import pycountry
from sentry_sdk import configure_scope


def is_country_name(country_name: str) -> bool:
    try:
        pycountry.countries.lookup(country_name)
        return True
    except LookupError:
        return False


class SentryScopeMiddleware:
    business_area: str = "NO_BA"

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        super().__init__()

    # Note: must be listed AFTER AuthenticationMiddleware
    def __call__(self, request: HttpRequest) -> Any:
        sys.stderr.isatty = lambda: False  # type: ignore # I guess this is a hack to make Sentry not use colors in the terminal?
        with configure_scope() as scope:
            business_area = request.headers.get("Business-Area")
            if not business_area:
                # example: api/rest/ukraine/rdi/upload/; api/admin/account/role/;
                # all api urls with BA has pattern 'api/rest/BA/etc'
                pattern = r"api/rest/(?P<country>[^/]+)/"
                match = re.search(pattern, request.path)
                business_area = match.group("country") if match else self.business_area
            scope.set_tag("username", request.user.username)
            scope.set_tag("business_area", business_area)
            return self.get_response(request)
