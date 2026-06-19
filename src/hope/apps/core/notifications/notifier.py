from typing import Any, Protocol

from hope.apps.core.notifications.bitcaster_client import BitcasterClient


class NotificationBackend(Protocol):
    is_configured: bool

    def trigger_event(
        self,
        event_name: str,
        payload: dict[str, Any],
        options: dict[str, Any] | None = None,
        cid: str | None = None,
    ) -> bool: ...


def get_notification_backend() -> NotificationBackend:
    return BitcasterClient()


def send_notification_event(
    event_name: str,
    payload: dict[str, Any],
    options: dict[str, Any] | None = None,
    cid: str | None = None,
) -> bool:
    backend = get_notification_backend()
    return backend.trigger_event(event_name, payload, options=options, cid=cid)
