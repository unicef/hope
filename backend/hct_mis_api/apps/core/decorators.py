from django.core.cache import cache


def cached_in_django_cache(timeout_in_hours):
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}_{kwargs}"
            value = cache.get(key)
            if value is not None:
                return value
            else:
                value = func(*args, **kwargs)
                cache.set(key, value, timeout_in_hours * 60 * 60)
                return value

        return wrapper

    return decorator
