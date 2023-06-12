from typing import Any


class QueryRunError(Exception):
    def __init__(
        self,
        exception: Exception,
        sentry_error_id: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.exception = exception
        self.sentry_error_id = sentry_error_id

    def __str__(self) -> str:
        return str(f"{self.exception.__class__.__name__}: {self.exception}")
