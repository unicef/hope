from typing import Any


class QueryRunError(BaseException):
    def __init__(self, exception: BaseException, sentry_error_id: Any = None, *args: Any, **kwargs: Any) -> None:
        self.exception = exception
        self.sentry_error_id = sentry_error_id

    def __str__(self) -> str:
        return str(self.exception)
