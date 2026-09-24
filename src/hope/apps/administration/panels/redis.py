from typing import Any

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from smart_admin.console import panel_redis as smart_panel_redis


def panel_redis(self: Any, request: HttpRequest, extra_context: dict | None = None) -> HttpResponse:
    if not request.user.is_superuser:
        raise PermissionDenied
    return smart_panel_redis(self, request, extra_context)


panel_redis.verbose_name = smart_panel_redis.verbose_name
