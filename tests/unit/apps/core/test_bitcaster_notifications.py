from types import SimpleNamespace
from typing import Any

from celery.exceptions import Retry
from django.test import override_settings
import pytest

from hope.apps.core.notifications.bitcaster_client import BitcasterClient, BitcasterClientConfig
from hope.apps.core.notifications.flags import bitcaster_enabled
from hope.apps.core.notifications.handlers import handle_bitcaster_event
from hope.apps.core.notifications.payloads import (
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
        "payment.plan.sent_for_approval",
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
        "event": "payment.plan.sent_for_approval",
        "context": {"correlation_id": "event:1"},
        "options": {"limit_to": ["user@example.org"]},
        "cid": "event:1",
    }
    assert sdk_client.request_kwargs == {"timeout": 7}


def test_publish_mailjet_template_email_event_sends_payload_to_signal(mocker: Any) -> None:
    mock_signal_send = mocker.patch("hope.apps.core.notifications.publishers.bitcaster_event_signal.send")

    publish_mailjet_template_email_event(
        MailjetTemplateEmailEvent(
            event_name="payment.plan.sent_for_approval",
            idempotency_key="payment.plan.sent_for_approval:1:SEND_FOR_APPROVAL",
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
    assert mock_signal_send.call_args.kwargs["event_name"] == "payment.plan.sent_for_approval"
    assert payload["idempotency_key"] == "payment.plan.sent_for_approval:1:SEND_FOR_APPROVAL"
    assert payload["options"] == {"limit_to": ["approver@example.org"]}


def test_build_rendered_email_payload_limits_bitcaster_delivery_to_recipients() -> None:
    payload = build_rendered_email_payload(
        RenderedEmailPayloadData(
            idempotency_key="email.rendered.sent:service:1",
            recipients=["user@example.org"],
            subject="Rendered subject",
            html_body="<p>Rendered</p>",
            text_body="Rendered",
            html_template="email.html",
            text_template="email.txt",
            context={"title": "Rendered subject"},
            metadata={"service": "Service"},
        )
    )

    assert payload["correlation_id"] == "email.rendered.sent:service:1"
    assert payload["provider"] == "rendered"
    assert payload["recipients"] == ["user@example.org"]
    assert payload["html_template"] == "email.html"
    assert payload["text_template"] == "email.txt"
    assert payload["context"] == {"title": "Rendered subject"}
    assert payload["options"] == {"limit_to": ["user@example.org"]}


def test_publish_rendered_email_event_sends_payload_to_signal(mocker: Any) -> None:
    mock_signal_send = mocker.patch("hope.apps.core.notifications.publishers.bitcaster_event_signal.send")

    publish_rendered_email_event(
        RenderedEmailEvent(
            event_name="email.rendered.sent",
            idempotency_key="email.rendered.sent:service:1",
            recipients=["user@example.org"],
            subject="Rendered subject",
            html_body="<p>Rendered</p>",
            text_body="Rendered",
            html_template="email.html",
            text_template="email.txt",
            context={"title": "Rendered subject"},
            metadata={"service": "Service"},
        )
    )

    payload = mock_signal_send.call_args.kwargs["payload"]
    mock_signal_send.assert_called_once()
    assert mock_signal_send.call_args.kwargs["event_name"] == "email.rendered.sent"
    assert payload["idempotency_key"] == "email.rendered.sent:service:1"
    assert payload["options"] == {"limit_to": ["user@example.org"]}


def test_publish_rendered_email_notification_skips_when_flag_disabled(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=False)
    mock_publish = mocker.patch("hope.apps.core.notifications.publishers.publish_rendered_email_event")

    class RenderedEmailService(BaseRenderedEmailNotificationService):
        html_template = "email.html"
        text_template = "email.txt"

    publish_rendered_email_notification(
        RenderedEmailNotification(
            service=RenderedEmailService(),
            user=SimpleNamespace(id=1, email="user@example.org"),
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
            service=RenderedEmailService(),
            user=SimpleNamespace(id=1, email="user@example.org"),
            subject="Rendered subject",
            html_body="<p>Rendered</p>",
            text_body="Rendered",
            context={"title": "Rendered subject"},
        )
    )

    event = mock_publish.call_args.args[0]
    assert event.event_name == "email.rendered.sent"
    assert event.recipients == ["user@example.org"]
    assert event.html_template == "email.html"
    assert event.text_template == "email.txt"
    assert event.metadata == {
        "source": "hope",
        "service": "tests.RenderedEmailService",
        "user_id": "1",
    }
    assert event.idempotency_key.startswith("email.rendered.sent:tests.RenderedEmailService:1:")


def test_base_rendered_email_notification_service_requires_templates() -> None:
    class MissingTextTemplateService(BaseRenderedEmailNotificationService):
        html_template = "email.html"

    with pytest.raises(NotImplementedError, match="text_template is required"):
        MissingTextTemplateService()


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
def test_bitcaster_enabled_reads_django_flags() -> None:
    assert bitcaster_enabled() is True


@override_settings(
    BITCASTER_EVENT_ALLOWLIST=["payment.plan.sent_for_approval"],
    FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]},
)
def test_handle_bitcaster_event_queues_allowed_event(mocker: Any) -> None:
    mock_delay = mocker.patch("hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay")
    payload = {"correlation_id": "event:1"}

    handle_bitcaster_event(sender=None, event_name="payment.plan.sent_for_approval", payload=payload)

    mock_delay.assert_called_once_with("payment.plan.sent_for_approval", payload)


@override_settings(
    BITCASTER_EVENT_ALLOWLIST=["payment.plan.approved"],
    FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]},
)
def test_handle_bitcaster_event_skips_events_outside_allowlist(mocker: Any) -> None:
    mock_delay = mocker.patch("hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay")

    handle_bitcaster_event(sender=None, event_name="payment.plan.sent_for_approval", payload={"correlation_id": "1"})

    mock_delay.assert_not_called()


def test_send_bitcaster_event_task_passes_options_and_correlation_id(mocker: Any) -> None:
    payload = {
        "correlation_id": "payment.plan.sent_for_approval:1:SEND_FOR_APPROVAL",
        "options": {"limit_to": ["approver@example.org"]},
    }
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=True)
    mocker.patch(
        "hope.apps.core.notifications.tasks.get_notification_backend",
        return_value=SimpleNamespace(is_configured=True),
    )
    mock_send = mocker.patch("hope.apps.core.notifications.tasks.send_notification_event", return_value=True)

    send_bitcaster_event_task("payment.plan.sent_for_approval", payload)

    mock_send.assert_called_once_with(
        "payment.plan.sent_for_approval",
        payload,
        options={"limit_to": ["approver@example.org"]},
        cid="payment.plan.sent_for_approval:1:SEND_FOR_APPROVAL",
    )


def test_send_bitcaster_event_task_retries_when_backend_returns_false(mocker: Any) -> None:
    payload = {"correlation_id": "payment.plan.sent_for_approval:1:SEND_FOR_APPROVAL", "options": {}}
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=True)
    mocker.patch(
        "hope.apps.core.notifications.tasks.get_notification_backend",
        return_value=SimpleNamespace(is_configured=True),
    )
    mocker.patch("hope.apps.core.notifications.tasks.send_notification_event", return_value=False)
    mock_retry = mocker.patch.object(send_bitcaster_event_task, "retry", side_effect=Retry())

    with pytest.raises(Retry):
        send_bitcaster_event_task("payment.plan.sent_for_approval", payload)

    mock_retry.assert_called_once()
