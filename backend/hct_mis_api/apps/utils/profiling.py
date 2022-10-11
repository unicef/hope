from functools import wraps

from django.conf import settings


def do_nothing_decorator(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapped


def profiling(**silk_kwargs):
    if not settings.PROFILING:
        return do_nothing_decorator

    from silk.profiling.profiler import (
        silk_profile,  # pylint: disable=import-outside-toplevel
    )

    return silk_profile(**silk_kwargs)
