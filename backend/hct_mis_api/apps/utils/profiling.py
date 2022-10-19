from functools import wraps
from types import FunctionType
from typing import Any, Dict, List

from django.conf import settings


def do_nothing_decorator(func: FunctionType) -> FunctionType:
    @wraps(func)
    def wrapped(*args: List, **kwargs: Dict) -> Any:
        return func(*args, **kwargs)

    return wrapped


def profiling(**silk_kwargs: Dict) -> Any:
    if not settings.PROFILING:
        return do_nothing_decorator

    from silk.profiling.profiler import (
        silk_profile,  # pylint: disable=import-outside-toplevel
    )

    return silk_profile(**silk_kwargs)
