from functools import wraps
from typing import Any, Callable, Dict, List

from sentry_sdk import configure_scope


def sentry_tags(func: Callable) -> Callable:
    """
    add sentry tags 'celery' and 'celery_task'
    """

    @wraps(func)
    def wrapper(*args: List, **kwargs: Any) -> Any:
        with configure_scope() as scope:
            scope.set_tag("celery", True)
            scope.set_tag("celery_task", func.__name__)

            return func(*args, **kwargs)

    return wrapper
