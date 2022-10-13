from functools import wraps

from sentry_sdk import configure_scope


def sentry_tags(func):
    """
    add sentry tags 'celery' and 'celery_task'
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        with configure_scope() as scope:
            scope.set_tag("celery", True)
            scope.set_tag("celery_task", func.__name__)

            return func(*args, **kwargs)

    return wrapper
