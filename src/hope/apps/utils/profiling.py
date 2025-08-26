from functools import wraps
from typing import Any, Callable

from django.conf import settings


def do_nothing_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapped


def profiling(**silk_kwargs: Any) -> Any:
    if not settings.PROFILING:
        return do_nothing_decorator

    from silk.profiling.profiler import (  # pylint: disable=import-outside-toplevel
        silk_profile,
    )

    return silk_profile(**silk_kwargs)
