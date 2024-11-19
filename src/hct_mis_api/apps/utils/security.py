from typing import Any

from django.conf import settings


def is_root(request: Any, *args: Any, **kwargs: Any) -> bool:
    return request.user.is_superuser and request.headers.get("x-root-token") == settings.ROOT_TOKEN


def can_hijack(hijacker: Any, hijacked: bool) -> bool:
    return hijacker.is_superuser
