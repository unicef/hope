from typing import Any, Protocol

from hope.apps.core.notifications.bitcaster_client import BitcasterClient


class NotificationBackend(Protocol):
    @property
    def is_configured(self) -> bool:
        raise NotImplementedError

    def trigger_event(
        self,
        event_name: str,
        payload: dict[str, Any],
        options: dict[str, Any] | None = None,
        cid: str | None = None,
    ) -> bool:
        raise NotImplementedError


def get_notification_backend() -> NotificationBackend:
    return BitcasterClient()
