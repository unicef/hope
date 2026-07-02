import logging
from typing import Any

from django.conf import settings
from django.dispatch import receiver

from hope.apps.core.notifications.flags import bitcaster_enabled
from hope.apps.core.notifications.signals import bitcaster_event_signal
from hope.apps.core.notifications.tasks import send_bitcaster_event_task

logger = logging.getLogger(__name__)


def _event_is_allowed(event_name: str) -> bool:
    allowlist = settings.BITCASTER_EVENT_ALLOWLIST
    return not allowlist or event_name in allowlist


@receiver(bitcaster_event_signal)
def handle_bitcaster_event(sender: Any, **kwargs: Any) -> None:
    event_name = kwargs["event_name"]
    payload = kwargs["payload"]

    if not bitcaster_enabled():
        logger.debug("Skipping Bitcaster event '%s': integration disabled.", event_name)
        return

    if not _event_is_allowed(event_name):
        logger.debug("Skipping Bitcaster event '%s': not in allowlist.", event_name)
        return

    send_bitcaster_event_task.delay(event_name, payload)
