from dataclasses import dataclass, field
import hashlib
import logging
from typing import Any

from hope.apps.core.notifications.events import RENDERED_EMAIL_SENT
from hope.apps.core.notifications.flags import bitcaster_enabled
from hope.apps.core.notifications.payloads import (
    MailjetTemplateEmailPayloadData,
    RenderedEmailPayloadData,
    build_mailjet_template_email_payload,
    build_rendered_email_payload,
)
from hope.apps.core.notifications.signals import bitcaster_event_signal

logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class MailjetTemplateEmailEvent:
    event_name: str
    idempotency_key: str
    recipients: list[str]
    subject: str
    mailjet_template_id: int
    variables: dict[str, Any]
    ccs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class RenderedEmailEvent:
    event_name: str
    idempotency_key: str
    recipients: list[str]
    subject: str
    html_body: str
    text_body: str
    html_template: str
    text_template: str
    context: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseRenderedEmailNotificationService:
    html_template: str
    text_template: str

    def __init__(self) -> None:
        if not getattr(self, "html_template", None):
            raise NotImplementedError("html_template is required")
        if not getattr(self, "text_template", None):
            raise NotImplementedError("text_template is required")


@dataclass(frozen=True, kw_only=True)
class RenderedEmailNotification:
    service: BaseRenderedEmailNotificationService
    user: Any
    subject: str
    html_body: str
    text_body: str
    context: dict[str, Any]


def publish_mailjet_template_email_event(event: MailjetTemplateEmailEvent) -> None:
    payload = build_mailjet_template_email_payload(
        MailjetTemplateEmailPayloadData(
            idempotency_key=event.idempotency_key,
            recipients=event.recipients,
            subject=event.subject,
            mailjet_template_id=event.mailjet_template_id,
            variables=event.variables,
            ccs=event.ccs,
            metadata=event.metadata,
        )
    )
    bitcaster_event_signal.send(
        sender=publish_mailjet_template_email_event,
        event_name=event.event_name,
        payload=payload,
    )


def publish_rendered_email_event(event: RenderedEmailEvent) -> None:
    payload = build_rendered_email_payload(
        RenderedEmailPayloadData(
            idempotency_key=event.idempotency_key,
            recipients=event.recipients,
            subject=event.subject,
            html_body=event.html_body,
            text_body=event.text_body,
            html_template=event.html_template,
            text_template=event.text_template,
            context=event.context,
            metadata=event.metadata,
        )
    )
    bitcaster_event_signal.send(
        sender=publish_rendered_email_event,
        event_name=event.event_name,
        payload=payload,
    )


def publish_rendered_email_notification(notification: RenderedEmailNotification) -> None:
    if not bitcaster_enabled():
        return

    try:
        publish_rendered_email_event(
            RenderedEmailEvent(
                event_name=RENDERED_EMAIL_SENT,
                idempotency_key=_build_rendered_email_idempotency_key(notification),
                recipients=[notification.user.email],
                subject=notification.subject,
                html_body=notification.html_body,
                text_body=notification.text_body,
                html_template=notification.service.html_template,
                text_template=notification.service.text_template,
                context=notification.context,
                metadata={
                    "source": "hope",
                    "service": _get_service_path(notification.service),
                    "user_id": str(notification.user.id),
                },
            )
        )
    except Exception:
        logger.exception("Failed to queue rendered email Bitcaster event")


def _build_rendered_email_idempotency_key(notification: RenderedEmailNotification) -> str:
    user_id = str(
        getattr(notification.user, "id", "")
        or getattr(notification.user, "pk", "")
        or getattr(notification.user, "email", "")
    )
    source = "|".join(
        [
            _get_service_path(notification.service),
            user_id,
            notification.service.html_template,
            notification.service.text_template,
            notification.subject,
            notification.html_body,
            notification.text_body,
        ]
    )
    digest = hashlib.sha256(source.encode()).hexdigest()[:16]
    return f"email.rendered.sent:{_get_service_path(notification.service)}:{user_id}:{digest}"


def _get_service_path(service: Any) -> str:
    return f"{service.__class__.__module__}.{service.__class__.__name__}"
