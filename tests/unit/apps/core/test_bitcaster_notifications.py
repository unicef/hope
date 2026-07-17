from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Any
from uuid import UUID

from celery.exceptions import Retry
from django.test import override_settings
import pytest

from hope.apps.core.notifications.bitcaster_client import BitcasterClient, BitcasterClientConfig
from hope.apps.core.notifications.flags import bitcaster_enabled
from hope.apps.core.notifications.handlers import handle_bitcaster_event
from hope.apps.core.notifications.notifier import NotificationBackend, get_notification_backend, send_notification_event
from hope.apps.core.notifications.payloads import (
    EmailAttachmentPayload,
    MailjetTemplateEmailPayloadData,
    RenderedEmailPayloadData,
    build_mailjet_template_email_payload,
    build_rendered_email_payload,
)
from hope.apps.core.notifications.publishers import (
    BaseRenderedEmailNotificationService,
    MailjetTemplateEmailEvent,
    RenderedEmailEvent,
    RenderedEmailNotification,
    publish_mailjet_template_email_event,
    publish_rendered_email_event,
    publish_rendered_email_notification,
)
from hope.apps.core.notifications.tasks import send_bitcaster_event_task

pytestmark = pytest.mark.django_db


class FakeBitcasterSDKClient:
    last_instance = None

    def __init__(self, bae: str):
        self.bae = bae
        self.transport = SimpleNamespace(
            session=SimpleNamespace(request=self.request),
        )
        self.request_kwargs = None
        self.trigger_kwargs = None
        FakeBitcasterSDKClient.last_instance = self

    def request(self, method: str, url: str, **kwargs: Any) -> SimpleNamespace:
        self.request_kwargs = kwargs
        return SimpleNamespace(status_code=200)

    def trigger(self, **kwargs: Any) -> None:
        self.trigger_kwargs = kwargs
        self.transport.session.request("POST", "https://bitcaster.example.org/trigger/")


def test_build_mailjet_template_email_payload_limits_bitcaster_delivery_to_recipients() -> None:
    payload = build_mailjet_template_email_payload(
        MailjetTemplateEmailPayloadData(
            idempotency_key="event:1",
            recipients=["first@example.org", "second@example.org"],
            subject="Subject",
            mailjet_template_id=123,
            variables={"name": "Jane"},
            ccs=["actor@example.org"],
            metadata={"source": "hope"},
        )
    )

    assert payload["correlation_id"] == "event:1"
    assert payload["recipients"] == ["first@example.org", "second@example.org"]
    assert payload["cc"] == ["actor@example.org"]
    assert payload["metadata"] == {"source": "hope"}
    assert payload["options"] == {"limit_to": ["first@example.org", "second@example.org"]}


def test_bitcaster_client_configures_sdk_request_timeout(mocker: Any) -> None:
    mocker.patch("bitcaster_sdk.client.Client", FakeBitcasterSDKClient)
    client = BitcasterClient(
        BitcasterClientConfig(
            api_url="https://bitcaster.example.org",
            api_key="api-key",
            organization_slug="unicef",
            project_slug="hope",
            application_slug="hct-mis",
            request_timeout=7,
        )
    )

    result = client.trigger_event(
        "payment.payment_plan.sent_for_approval",
        {"correlation_id": "event:1"},
        options={"limit_to": ["user@example.org"]},
        cid="event:1",
    )

    sdk_client = FakeBitcasterSDKClient.last_instance
    assert result is True
    assert sdk_client.bae == "https://api-key@bitcaster.example.org/api/o/unicef/"
    assert sdk_client.trigger_kwargs == {
        "project": "hope",
        "application": "hct-mis",
        "event": "payment.payment_plan.sent_for_approval",
        "context": {"correlation_id": "event:1"},
        "options": {"limit_to": ["user@example.org"]},
        "cid": "event:1",
    }
    assert sdk_client.request_kwargs == {"timeout": 7}


def test_bitcaster_client_returns_false_when_unconfigured() -> None:
    client = BitcasterClient(
        BitcasterClientConfig(
            api_url="",
            api_key="",
            organization_slug="",
            project_slug="",
            application_slug="",
        )
    )

    assert client.trigger_event("payment.payment_plan.sent_for_approval", {"correlation_id": "event:1"}) is False


def test_publish_mailjet_template_email_event_sends_payload_to_signal(mocker: Any) -> None:
    mock_signal_send = mocker.patch("hope.apps.core.notifications.publishers.bitcaster_event_signal.send")

    publish_mailjet_template_email_event(
        MailjetTemplateEmailEvent(
            event_name="payment.payment_plan.sent_for_approval",
            idempotency_key="payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL",
            recipients=["approver@example.org"],
            subject="Payment pending for Approval",
            mailjet_template_id=123,
            variables={"payment_plan_id": "PP-1"},
            ccs=["actor@example.org"],
            metadata={"payment_plan_id": "1"},
        )
    )

    payload = mock_signal_send.call_args.kwargs["payload"]
    mock_signal_send.assert_called_once()
    assert mock_signal_send.call_args.kwargs["event_name"] == "payment.payment_plan.sent_for_approval"
    assert payload["idempotency_key"] == "payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL"
    assert payload["options"] == {"limit_to": ["approver@example.org"]}


def test_build_rendered_email_payload_limits_bitcaster_delivery_to_recipients() -> None:
    payload = build_rendered_email_payload(
        RenderedEmailPayloadData(
            idempotency_key="test.rendered_email.sent:service:1",
            recipients=["user@example.org"],
            subject="Rendered subject",
            html_body="<p>Rendered</p>",
            text_body="Rendered",
            html_template="email.html",
            text_template="email.txt",
            context={"title": "Rendered subject"},
            ccs=["cc@example.org"],
            metadata={"service": "Service"},
        )
    )

    assert payload["correlation_id"] == "test.rendered_email.sent:service:1"
    assert payload["provider"] == "rendered"
    assert payload["recipients"] == ["user@example.org"]
    assert payload["cc"] == ["cc@example.org"]
    assert payload["html_template"] == "email.html"
    assert payload["text_template"] == "email.txt"
    assert payload["context"] == {"title": "Rendered subject"}
    assert payload["options"] == {"limit_to": ["user@example.org"]}


def test_email_attachment_payload_serializes_with_asdict() -> None:
    attachment = EmailAttachmentPayload(
        filename="results.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        base64_content="base64-content",
    )

    assert asdict(attachment) == {
        "filename": "results.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "base64_content": "base64-content",
    }


def test_publish_rendered_email_event_sends_payload_to_signal(mocker: Any) -> None:
    mock_signal_send = mocker.patch("hope.apps.core.notifications.publishers.bitcaster_event_signal.send")

    publish_rendered_email_event(
        RenderedEmailEvent(
            event_name="test.rendered_email.sent",
            idempotency_key="test.rendered_email.sent:service:1",
            recipients=["user@example.org"],
            subject="Rendered subject",
            html_body="<p>Rendered</p>",
            text_body="Rendered",
            html_template="email.html",
            text_template="email.txt",
            context={"title": "Rendered subject"},
            ccs=["cc@example.org"],
            metadata={"service": "Service"},
        )
    )

    payload = mock_signal_send.call_args.kwargs["payload"]
    mock_signal_send.assert_called_once()
    assert mock_signal_send.call_args.kwargs["event_name"] == "test.rendered_email.sent"
    assert payload["idempotency_key"] == "test.rendered_email.sent:service:1"
    assert payload["cc"] == ["cc@example.org"]
    assert payload["options"] == {"limit_to": ["user@example.org"]}


def test_publish_rendered_email_notification_skips_when_flag_disabled(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=False)
    mock_publish = mocker.patch("hope.apps.core.notifications.publishers.publish_rendered_email_event")

    class RenderedEmailService(BaseRenderedEmailNotificationService):
        html_template = "email.html"
        text_template = "email.txt"

    publish_rendered_email_notification(
        RenderedEmailNotification(
            event_name="test.rendered_email.sent",
            service=RenderedEmailService(),
            recipient_email="user@example.org",
            subject="Rendered subject",
            html_body="<p>Rendered</p>",
            text_body="Rendered",
            context={"title": "Rendered subject"},
        )
    )

    mock_publish.assert_not_called()


def test_publish_rendered_email_notification_publishes_when_flag_enabled(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=True)
    mock_publish = mocker.patch("hope.apps.core.notifications.publishers.publish_rendered_email_event")

    class RenderedEmailService(BaseRenderedEmailNotificationService):
        html_template = "email.html"
        text_template = "email.txt"

    RenderedEmailService.__module__ = "tests"
    publish_rendered_email_notification(
        RenderedEmailNotification(
            event_name="test.rendered_email.sent",
            service=RenderedEmailService(),
            recipient_email="user@example.org",
            subject="Rendered subject",
            html_body="<p>Rendered</p>",
            text_body="Rendered",
            context={"title": "Rendered subject"},
        )
    )

    event = mock_publish.call_args.args[0]
    assert event.event_name == "test.rendered_email.sent"
    assert event.recipients == ["user@example.org"]
    assert event.html_template == "email.html"
    assert event.text_template == "email.txt"
    assert event.metadata == {
        "source": "hope",
        "service": "tests.RenderedEmailService",
    }
    assert event.idempotency_key.startswith("test.rendered_email.sent:tests.RenderedEmailService:user@example.org:")


def test_publish_rendered_email_notification_normalizes_context_to_json_safe_values(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=True)
    mock_publish = mocker.patch("hope.apps.core.notifications.publishers.publish_rendered_email_event")

    class UnknownContextValue:
        def __str__(self) -> str:
            return "unknown-context-value"

    class RenderedEmailService(BaseRenderedEmailNotificationService):
        html_template = "email.html"
        text_template = "email.txt"

    publish_rendered_email_notification(
        RenderedEmailNotification(
            event_name="test.rendered_email.sent",
            service=RenderedEmailService(),
            recipient_email="user@example.org",
            subject="Rendered subject",
            html_body="<p>Rendered</p>",
            text_body="Rendered",
            context={
                "date": date(2050, 1, 2),
                "expires_at": datetime(2050, 1, 1, 12, 30, 0),
                "uuid": UUID("12345678-1234-5678-1234-567812345678"),
                "decimal": Decimal("123.45"),
                "custom": UnknownContextValue(),
                "nested": {
                    "date": date(2051, 2, 3),
                    "values": [Decimal("1.25"), UUID("87654321-4321-8765-4321-876543218765")],
                    "custom": UnknownContextValue(),
                },
            },
        )
    )

    event = mock_publish.call_args.args[0]
    assert event.context == {
        "date": "2050-01-02",
        "expires_at": "2050-01-01 12:30:00",
        "uuid": "12345678-1234-5678-1234-567812345678",
        "decimal": "123.45",
        "custom": "unknown-context-value",
        "nested": {
            "date": "2051-02-03",
            "values": ["1.25", "87654321-4321-8765-4321-876543218765"],
            "custom": "unknown-context-value",
        },
    }


def test_publish_rendered_email_notification_swallows_publish_error(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=True)
    mocker.patch(
        "hope.apps.core.notifications.publishers.publish_rendered_email_event",
        side_effect=RuntimeError("queue failed"),
    )

    class RenderedEmailService(BaseRenderedEmailNotificationService):
        html_template = "email.html"
        text_template = "email.txt"

    publish_rendered_email_notification(
        RenderedEmailNotification(
            event_name="test.rendered_email.sent",
            service=RenderedEmailService(),
            recipient_email="user@example.org",
            subject="Rendered subject",
            html_body="<p>Rendered</p>",
            text_body="Rendered",
            context={"title": "Rendered subject"},
        )
    )


def test_base_rendered_email_notification_service_requires_templates() -> None:
    class MissingTextTemplateService(BaseRenderedEmailNotificationService):
        html_template = "email.html"

    with pytest.raises(NotImplementedError, match="text_template is required"):
        MissingTextTemplateService()


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
def test_bitcaster_enabled_reads_django_flags() -> None:
    assert bitcaster_enabled() is True


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": False}]})
def test_handle_bitcaster_event_skips_when_flag_disabled(mocker: Any) -> None:
    mock_delay = mocker.patch("hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay")

    handle_bitcaster_event(
        sender=None,
        event_name="payment.payment_plan.sent_for_approval",
        payload={"correlation_id": "1"},
    )

    mock_delay.assert_not_called()


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
def test_handle_bitcaster_event_queues_allowed_event(mocker: Any) -> None:
    mock_delay = mocker.patch("hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay")
    payload = {"correlation_id": "event:1"}

    handle_bitcaster_event(sender=None, event_name="payment.payment_plan.sent_for_approval", payload=payload)

    mock_delay.assert_called_once_with("payment.payment_plan.sent_for_approval", payload)


def test_send_bitcaster_event_task_passes_options_and_correlation_id(mocker: Any) -> None:
    payload = {
        "correlation_id": "payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL",
        "options": {"limit_to": ["approver@example.org"]},
    }
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=True)
    mocker.patch(
        "hope.apps.core.notifications.tasks.get_notification_backend",
        return_value=SimpleNamespace(is_configured=True),
    )
    mock_send = mocker.patch("hope.apps.core.notifications.tasks.send_notification_event", return_value=True)

    send_bitcaster_event_task("payment.payment_plan.sent_for_approval", payload)

    mock_send.assert_called_once_with(
        "payment.payment_plan.sent_for_approval",
        payload,
        options={"limit_to": ["approver@example.org"]},
        cid="payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL",
    )


def test_send_bitcaster_event_task_skips_when_flag_disabled(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=False)
    mock_backend = mocker.patch("hope.apps.core.notifications.tasks.get_notification_backend")

    send_bitcaster_event_task("payment.payment_plan.sent_for_approval", {"correlation_id": "1"})

    mock_backend.assert_not_called()


def test_send_bitcaster_event_task_skips_when_backend_not_configured(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=True)
    mocker.patch(
        "hope.apps.core.notifications.tasks.get_notification_backend",
        return_value=SimpleNamespace(is_configured=False),
    )
    mock_send = mocker.patch("hope.apps.core.notifications.tasks.send_notification_event")

    send_bitcaster_event_task("payment.payment_plan.sent_for_approval", {"correlation_id": "1"})

    mock_send.assert_not_called()


def test_send_bitcaster_event_task_retries_when_backend_returns_false(mocker: Any) -> None:
    payload = {"correlation_id": "payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL", "options": {}}
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=True)
    mocker.patch(
        "hope.apps.core.notifications.tasks.get_notification_backend",
        return_value=SimpleNamespace(is_configured=True),
    )
    mocker.patch("hope.apps.core.notifications.tasks.send_notification_event", return_value=False)
    mock_retry = mocker.patch.object(send_bitcaster_event_task, "retry", side_effect=Retry())

    with pytest.raises(Retry):
        send_bitcaster_event_task("payment.payment_plan.sent_for_approval", payload)

    mock_retry.assert_called_once()


def test_send_bitcaster_event_task_retries_unexpected_exception(mocker: Any) -> None:
    payload = {"correlation_id": "payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL", "options": {}}
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=True)
    mocker.patch(
        "hope.apps.core.notifications.tasks.get_notification_backend",
        return_value=SimpleNamespace(is_configured=True),
    )
    mocker.patch("hope.apps.core.notifications.tasks.send_notification_event", side_effect=RuntimeError("boom"))
    mock_retry = mocker.patch.object(send_bitcaster_event_task, "retry", side_effect=Retry())

    with pytest.raises(Retry):
        send_bitcaster_event_task("payment.payment_plan.sent_for_approval", payload)

    mock_retry.assert_called_once()


def test_get_notification_backend_returns_bitcaster_client() -> None:
    assert isinstance(get_notification_backend(), BitcasterClient)


def test_notification_backend_protocol_stub_methods_are_covered() -> None:
    with pytest.raises(NotImplementedError):
        NotificationBackend.is_configured.fget(SimpleNamespace())

    with pytest.raises(NotImplementedError):
        NotificationBackend.trigger_event(
            SimpleNamespace(),
            "payment.payment_plan.sent_for_approval",
            {"correlation_id": "1"},
            options={"limit_to": ["user@example.org"]},
            cid="1",
        )


def test_send_notification_event_delegates_to_backend(mocker: Any) -> None:
    backend = SimpleNamespace(trigger_event=mocker.Mock(return_value=True))
    mocker.patch("hope.apps.core.notifications.notifier.get_notification_backend", return_value=backend)

    assert (
        send_notification_event(
            "payment.payment_plan.sent_for_approval",
            {"correlation_id": "1"},
            options={"limit_to": ["user@example.org"]},
            cid="1",
        )
        is True
    )
    backend.trigger_event.assert_called_once_with(
        "payment.payment_plan.sent_for_approval",
        {"correlation_id": "1"},
        options={"limit_to": ["user@example.org"]},
        cid="1",
    )
