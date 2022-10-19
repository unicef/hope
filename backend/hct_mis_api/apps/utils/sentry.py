from functools import wraps
from types import FunctionType
from typing import Any, Dict, List

from sentry_sdk import configure_scope


def sentry_tags(func) -> FunctionType:
    """
    add sentry tags 'celery' and 'celery_task'
    """

    @wraps(func)
    def wrapper(*args: List, **kwargs: Dict) -> Any:
        with configure_scope() as scope:
            scope.set_tag("celery", True)
            scope.set_tag("celery_task", func.__name__)

            return func(*args, **kwargs)

    return wrapper
