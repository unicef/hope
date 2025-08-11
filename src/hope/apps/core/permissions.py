from typing import Any, Callable

from django.core.exceptions import PermissionDenied


def is_authenticated(func: Callable) -> Any:
    """
    Simple decorator for use with Graphene mutate method
    to check if user is authenticated.
    """

    def wrapper(cls: Any, root: Any, info: Any, *args: Any, **kwargs: Any) -> Any:
        if not info.context.user.is_authenticated:
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        return func(cls, root, info, *args, **kwargs)

    return wrapper
