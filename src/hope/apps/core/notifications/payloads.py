from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, kw_only=True)
class MailjetTemplateEmailPayloadData:
    idempotency_key: str
    recipients: list[str]
    subject: str
    mailjet_template_id: int
    variables: dict[str, Any]
    ccs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class RenderedEmailPayloadData:
    idempotency_key: str
    recipients: list[str]
    subject: str
    html_body: str
    text_body: str
    html_template: str
    text_template: str
    context: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


def build_mailjet_template_email_payload(data: MailjetTemplateEmailPayloadData) -> dict[str, Any]:
    return {
        "idempotency_key": data.idempotency_key,
        "correlation_id": data.idempotency_key,
        "channel": "email",
        "provider": "mailjet",
        "recipients": data.recipients,
        "cc": data.ccs,
        "subject": data.subject,
        "mailjet_template_id": data.mailjet_template_id,
        "variables": data.variables,
        "metadata": data.metadata,
        "options": {
            "limit_to": data.recipients,
        },
    }


def build_rendered_email_payload(data: RenderedEmailPayloadData) -> dict[str, Any]:
    return {
        "idempotency_key": data.idempotency_key,
        "correlation_id": data.idempotency_key,
        "channel": "email",
        "provider": "rendered",
        "recipients": data.recipients,
        "cc": [],
        "subject": data.subject,
        "html_body": data.html_body,
        "text_body": data.text_body,
        "html_template": data.html_template,
        "text_template": data.text_template,
        "context": data.context,
        "metadata": data.metadata,
        "options": {
            "limit_to": data.recipients,
        },
    }
