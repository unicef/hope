from typing import Any

from django.http import HttpRequest
from django.test import RequestFactory

from hope.models import User


def admin_request(user: User, params: dict[str, Any] | None = None) -> HttpRequest:
    request = RequestFactory().get("/admin/", params or {})
    request.user = user
    return request
