from typing import Any, Callable

from django.core.exceptions import PermissionDenied


def is_authenticated(func: Callable) -> Any:
    """Check if user is authenticated [Decorator]."""

    def wrapper(cls: Any, root: Any, info: Any, *args: Any, **kwargs: Any) -> Any:
        if not info.context.user.is_authenticated:
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        return func(cls, root, info, *args, **kwargs)

    return wrapper
