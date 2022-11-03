from functools import wraps
from typing import Any, Callable, Dict

from django.conf import settings


def do_nothing_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapped


def profiling(**silk_kwargs: Dict) -> Any:
    if not settings.PROFILING:
        return do_nothing_decorator

    from silk.profiling.profiler import (
        silk_profile,  # pylint: disable=import-outside-toplevel
    )

    return silk_profile(**silk_kwargs)
