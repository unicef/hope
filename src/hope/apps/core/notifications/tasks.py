import logging
from typing import Any

from celery import Task

from hope.apps.core.celery import app
from hope.apps.core.notifications.flags import bitcaster_enabled
from hope.apps.core.notifications.notifier import get_notification_backend

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
def send_bitcaster_event_task(self: Task, event_name: str, payload: dict[str, Any], correlation_id: str) -> None:
    if not bitcaster_enabled():
        return

    backend = get_notification_backend()
    if not backend.is_configured:
        logger.warning("Skipping Bitcaster task: client not configured (event='%s').", event_name)
        return

    try:
        success = backend.trigger_event(
            event_name,
            payload,
            options=payload.get("options") or {},
            cid=correlation_id,
        )
    except Exception as exc:
        logger.exception("Bitcaster send failed for event '%s'.", event_name)
        raise self.retry(exc=exc)

    if not success:
        logger.warning("Bitcaster client returned false for event '%s'.", event_name)
        raise self.retry(exc=RuntimeError(f"Bitcaster client returned false for event '{event_name}'"))
