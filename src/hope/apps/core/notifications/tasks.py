import logging
from typing import Any

from celery import Task

from hope.apps.core.celery import app
from hope.apps.core.notifications.flags import bitcaster_enabled
from hope.apps.core.notifications.notifier import get_notification_backend, send_notification_event

logger = logging.getLogger(__name__)


class NotifyError(Exception):
    pass


@app.task(bind=True, default_retry_delay=60, max_retries=3)
def send_bitcaster_event_task(self: Task, event_name: str, payload: dict[str, Any]) -> None:
    if not bitcaster_enabled():
        return

    backend = get_notification_backend()
    if not backend.is_configured:
        logger.warning("Skipping Bitcaster task: client not configured (event='%s').", event_name)
        return

    try:
        success = send_notification_event(
            event_name,
            payload,
            options=payload.get("options") or {},
            cid=payload["correlation_id"],
        )
        if not success:
            logger.warning("Bitcaster client returned false for event '%s'.", event_name)
            raise NotifyError(f"Bitcaster client returned false for event '{event_name}'")
    except NotifyError as exc:  # pragma: no cover
        logger.error("Bitcaster send failed for event '%s': %s", event_name, str(exc))
        raise self.retry(exc=exc)
    except Exception as exc:  # pragma: no cover
        logger.exception("Bitcaster send failed for event '%s'.", event_name)
        raise self.retry(exc=exc)
