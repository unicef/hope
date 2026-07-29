from collections.abc import Callable
from functools import wraps

from django.conf import settings


def test_conditional(decorator: Callable[..., object]) -> Callable[..., object]:
    """A conditional decorator that applies the inner decorator only if not in a test environment."""

    def conditional_decorator(fn: Callable[..., object]) -> Callable[..., object]:
        _decorated = decorator(fn)

        @wraps(fn)
        def wrapper(self, *args: object, **kwargs: object) -> object:
            if not settings.IS_TEST:
                return _decorated(self, *args, **kwargs)
            return fn(self, *args, **kwargs)

        return wrapper

    return conditional_decorator
