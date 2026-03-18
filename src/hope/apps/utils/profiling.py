from functools import wraps
from typing import Any, Callable, TypeVar

from django.conf import settings

F = TypeVar("F", bound=Callable[..., Any])


def do_nothing_decorator(func: F) -> F:
    @wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapped  # type: ignore[return-value]


def profiling(**silk_kwargs: Any) -> Callable[[F], F]:
    if not settings.PROFILING:
        return do_nothing_decorator

    from silk.profiling.profiler import (  # pylint: disable=import-outside-toplevel
        silk_profile,
    )

    return silk_profile(**silk_kwargs)
