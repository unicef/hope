from dataclasses import asdict
import hashlib
import json
import logging
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder

from hope.apps.core.notifications.flags import bitcaster_enabled
from hope.apps.core.notifications.payloads import EmailPayload
from hope.apps.core.notifications.signals import bitcaster_event_signal

logger = logging.getLogger(__name__)


def publish_email_notification(
    event_name: str,
    payload_data: EmailPayload,
    correlation_id: str | None = None,
) -> None:
    if not bitcaster_enabled():
        return

    try:
        _publish_email_notification(event_name, payload_data, correlation_id)
    except Exception:
        logger.exception("Failed to queue email Bitcaster event")


def _publish_email_notification(
    event_name: str,
    payload_data: EmailPayload,
    correlation_id: str | None = None,
) -> None:
    correlation_id = correlation_id or _build_email_correlation_id(event_name, payload_data)
    payload = asdict(payload_data)
    payload = _json_safe_context(payload)
    bitcaster_event_signal.send(
        sender=publish_email_notification,
        event_name=event_name,
        correlation_id=correlation_id,
        payload=payload,
    )


def _json_safe_context(context: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(context, cls=DjangoJSONEncoder, default=str))


def _build_email_correlation_id(event_name: str, payload_data: EmailPayload) -> str:
    source = json.dumps(
        {
            "event_name": event_name,
            "recipients": payload_data.recipients,
            "subject": payload_data.subject,
            "context": _json_safe_context(payload_data.context),
            "cc": payload_data.cc,
        },
        sort_keys=True,
    )
    digest = hashlib.sha256(source.encode()).hexdigest()[:16]
    return f"{event_name}:{':'.join(payload_data.recipients)}:{digest}"
