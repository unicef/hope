import logging
from typing import Any

from django.dispatch import receiver

from hope.apps.core.notifications.flags import bitcaster_enabled
from hope.apps.core.notifications.signals import bitcaster_event_signal
from hope.apps.core.notifications.tasks import send_bitcaster_event_task

logger = logging.getLogger(__name__)


@receiver(bitcaster_event_signal)
def handle_bitcaster_event(sender: Any, **kwargs: Any) -> None:
    event_name = kwargs["event_name"]
    correlation_id = kwargs["correlation_id"]
    payload = kwargs["payload"]

    if not bitcaster_enabled():
        logger.debug("Skipping Bitcaster event '%s': integration disabled.", event_name)
        return

    send_bitcaster_event_task.delay(event_name, payload, correlation_id)
