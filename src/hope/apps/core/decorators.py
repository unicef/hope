import hashlib
import json
from typing import Any, Callable

from django.core.cache import cache


def cached_in_django_cache(timeout_in_hours: int) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Callable:
            hashed_args = hashlib.sha256(json.dumps(kwargs).encode()).hexdigest()
            key = f"{func.__name__}_{hashed_args}"
            value = cache.get(key)
            if value is None:
                value = func(*args, **kwargs)
                cache.set(key, value, timeout_in_hours * 60 * 60)
            return value

        return wrapper

    return decorator
