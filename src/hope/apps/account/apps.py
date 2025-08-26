from typing import Any

from django.apps import AppConfig
from django.contrib.admin.options import get_content_type_for_model
from django.http import HttpRequest


class AccountConfig(AppConfig):
    name = "hope.apps.account"

    def ready(self) -> None:
        import hope.models  # noqa

        from hijack.signals import hijack_started

        import hope.apps.account.signals  # noqa

        hijack_started.connect(log_impersonate)


# TODO: LogEntry model is not available at this point, use narrower type
def log_impersonate(sender: Any, request: HttpRequest, hijacker: Any, hijacked: Any, *args: Any, **kwargs: Any) -> Any:
    from django.contrib.admin.models import LogEntry

    return LogEntry.objects.log_action(
        user_id=hijacker.pk,
        content_type_id=get_content_type_for_model(hijacked).pk,
        object_id=hijacked.pk,
        object_repr=str(hijacked),
        action_flag=0,
        change_message="impersonate",
    )
