from typing import Any
from django.apps import AppConfig
from django.contrib.admin.options import get_content_type_for_model


class AccountConfig(AppConfig):
    name = "hct_mis_api.apps.account"

    def ready(self) -> None:
        from hijack.signals import hijack_started

        hijack_started.connect(log_impersonate)


# TODO: LogEntry model is not available at this point, use narrower type
def log_impersonate(sender, request, hijacker, hijacked, *args, **kwargs) -> Any:
    from django.contrib.admin.models import LogEntry

    return LogEntry.objects.log_action(
        user_id=hijacker.pk,
        content_type_id=get_content_type_for_model(hijacked).pk,
        object_id=hijacked.pk,
        object_repr=str(hijacked),
        action_flag=0,
        change_message="impersonate",
    )
