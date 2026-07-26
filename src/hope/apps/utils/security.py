from typing import Any

from django.http import HttpRequest
from flags.state import flag_enabled


def is_root(request: HttpRequest, *args: Any, **kwargs: Any) -> bool:
    ret = False
    if hasattr(request, "user"):
        ret = request.user.is_superuser and flag_enabled("IS_ROOT", request=request)
    return ret


def can_hijack(hijacker: Any, hijacked: bool) -> bool:
    return hijacker.is_superuser
