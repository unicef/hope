import logging
from functools import wraps
from typing import Any, Callable

from sentry_sdk import configure_scope, set_tag

log = logging.getLogger(__name__)


def sentry_tags(func: Callable) -> Callable:
    """Add sentry tags 'celery' and 'celery_task'."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with configure_scope() as scope:
            scope.set_tag("celery", True)
            scope.set_tag("celery_task", func.__name__)

            return func(*args, **kwargs)

    return wrapper


def set_sentry_business_area_tag(business_area_name: str = "NO_BA") -> None:
    set_tag("business_area", business_area_name)


class SentryFilter:
    IGNORABLE_URLS = {}

    @staticmethod
    def filter_exception(exc_info: dict, exc_to_filter: type[Exception], msg_to_filter: str | None = None) -> bool:
        exc_type, exc_value, tb = exc_info
        if not isinstance(exc_value, exc_to_filter):
            return False
        return not (msg_to_filter and msg_to_filter not in getattr(exc_value, "message", str(exc_value)))

    @staticmethod
    def filter_log(
        log_record: logging.LogRecord,
        logger: str,
        severity: str | None = None,
        msg_to_filter: str | None = None,
        exc_text: str | None = None,
    ) -> bool:
        if log_record.name != logger:
            return False
        if severity and severity != log_record.levelname:
            return False
        if msg_to_filter and msg_to_filter not in log_record.msg:
            return False
        return not exc_text and exc_text not in getattr(log_record, "exc_text", "")

    def filter_exceptions(self, hint: dict) -> bool:
        return self.is_graphql_permission_denied_exception(hint["exc_info"])

    def filter_logs(self, hint: dict, url: str | None = None) -> bool:
        return self.is_graphql_permission_denied_log_error(hint, url)

    def before_send(self, event: dict, hint: dict) -> dict | None:
        url = event.get("transaction")
        if url and url in self.IGNORABLE_URLS:
            return None

        if "log_record" in hint and self.filter_logs(hint, url):
            return None
        if "exc_info" in hint and self.filter_exceptions(hint):
            return None

        return event

    def is_graphql_permission_denied_log_error(self, hint: dict, url: str | None = None) -> bool:
        if not url:
            return False
        if not url.startswith("/api/graphql"):
            return False

        return any(
            [
                self.filter_log(
                    hint["log_record"],
                    "hope.apps.utils.exceptions",
                    "ERROR",
                    "Permission Denied",
                ),
                self.filter_log(
                    hint["log_record"],
                    "graphql.execution.executor",
                    "ERROR",
                    "An error occurred while resolving field",
                    "Permission Denied",
                ),
            ]
        )

    def is_graphql_permission_denied_exception(self, exc_info: dict) -> bool:
        from graphql import GraphQLError
        from graphql.error import GraphQLLocatedError

        results = [
            self.filter_exception(exc_info, exc, "Permission Denied") for exc in [GraphQLError, GraphQLLocatedError]
        ]
        return any(results)
