from typing import Any, List


class QueryRunError(Exception):
    def __init__(self, exception: Exception, sentry_error_id: Any, *args: List, **kwargs: dict) -> None:
        self.exception = exception
        self.sentry_error_id = sentry_error_id

    def __str__(self) -> str:
        return str(self.exception)
