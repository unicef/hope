from typing import Any

from django.conf import settings
from django.http import HttpRequest


def is_root(request: HttpRequest, *args: Any, **kwargs: Any) -> bool:
    return request.user.is_superuser and request.headers.get("x-root-token") == settings.ROOT_TOKEN


def can_hijack(hijacker: object, hijacked: bool) -> bool:
    return hijacker.is_superuser
