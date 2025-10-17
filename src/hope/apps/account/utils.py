from functools import wraps
from typing import Any

from django.conf import settings


def test_conditional(decorator: Any) -> Any:
    """A conditional decorator that applies the inner decorator only if not in a test environment."""

    def conditional_decorator(fn: Any) -> Any:
        _decorated = decorator(fn)

        @wraps(fn)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            if not settings.IS_TEST:
                return _decorated(self, *args, **kwargs)
            return fn(self, *args, **kwargs)

        return wrapper

    return conditional_decorator
