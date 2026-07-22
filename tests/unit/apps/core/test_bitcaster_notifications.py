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
from hope.apps.core.notifications.notifier import NotificationBackend, get_notification_backend
from hope.apps.core.notifications.payloads import EmailPayload
from hope.apps.core.notifications.publishers import publish_email_notification
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


def test_publish_email_notification_limits_bitcaster_delivery_to_recipients(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=True)
    mock_signal_send = mocker.patch("hope.apps.core.notifications.publishers.bitcaster_event_signal.send")

    publish_email_notification(
        "test.email.sent",
        EmailPayload(
            recipients=["first@example.org", "second@example.org"],
            context={"name": "Jane"},
            cc=["actor@example.org"],
        ),
        correlation_id="event:1",
    )

    payload = mock_signal_send.call_args.kwargs["payload"]
    assert mock_signal_send.call_args.kwargs["correlation_id"] == "event:1"
    assert payload["recipients"] == ["first@example.org", "second@example.org"]
    assert payload["cc"] == ["actor@example.org"]
    assert payload["context"] == {"name": "Jane"}


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


def test_publish_email_notification_sends_payload_to_signal(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=True)
    mock_signal_send = mocker.patch("hope.apps.core.notifications.publishers.bitcaster_event_signal.send")

    publish_email_notification(
        "payment.payment_plan.sent_for_approval",
        EmailPayload(
            recipients=["approver@example.org"],
            context={"payment_plan_id": "PP-1"},
            cc=["actor@example.org"],
        ),
        correlation_id="payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL",
    )

    payload = mock_signal_send.call_args.kwargs["payload"]
    mock_signal_send.assert_called_once()
    assert mock_signal_send.call_args.kwargs["event_name"] == "payment.payment_plan.sent_for_approval"
    assert mock_signal_send.call_args.kwargs["correlation_id"] == (
        "payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL"
    )
    assert payload["context"] == {"payment_plan_id": "PP-1"}


def test_publish_email_notification_generates_idempotency_key(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=True)
    mock_signal_send = mocker.patch("hope.apps.core.notifications.publishers.bitcaster_event_signal.send")

    publish_email_notification(
        "test.email.sent",
        EmailPayload(
            recipients=["user@example.org"],
            context={"title": "Rendered subject"},
            cc=["cc@example.org"],
        ),
    )

    payload = mock_signal_send.call_args.kwargs["payload"]
    mock_signal_send.assert_called_once()
    assert mock_signal_send.call_args.kwargs["event_name"] == "test.email.sent"
    assert mock_signal_send.call_args.kwargs["correlation_id"].startswith("test.email.sent:user@example.org:")
    assert payload["cc"] == ["cc@example.org"]


def test_publish_email_notification_skips_when_flag_disabled(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=False)
    mock_signal_send = mocker.patch("hope.apps.core.notifications.publishers.bitcaster_event_signal.send")

    publish_email_notification(
        "test.email.sent",
        EmailPayload(
            recipients=["user@example.org"],
            context={"title": "Subject"},
        ),
    )

    mock_signal_send.assert_not_called()


def test_publish_email_notification_publishes_when_flag_enabled(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=True)
    mock_signal_send = mocker.patch("hope.apps.core.notifications.publishers.bitcaster_event_signal.send")

    publish_email_notification(
        "test.email.sent",
        EmailPayload(
            recipients=["user@example.org"],
            context={"title": "Subject"},
        ),
    )

    payload = mock_signal_send.call_args.kwargs["payload"]
    assert mock_signal_send.call_args.kwargs["event_name"] == "test.email.sent"
    assert payload["recipients"] == ["user@example.org"]
    assert "subject" not in payload
    assert payload["context"] == {"title": "Subject"}


def test_publish_email_notification_normalizes_context_to_json_safe_values(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=True)
    mock_signal_send = mocker.patch("hope.apps.core.notifications.publishers.bitcaster_event_signal.send")

    class UnknownContextValue:
        def __str__(self) -> str:
            return "unknown-context-value"

    publish_email_notification(
        "test.email.sent",
        EmailPayload(
            recipients=["user@example.org"],
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
        ),
    )

    payload = mock_signal_send.call_args.kwargs["payload"]
    assert payload["context"] == {
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


def test_publish_email_notification_swallows_publish_error(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.publishers.bitcaster_enabled", return_value=True)
    mocker.patch(
        "hope.apps.core.notifications.publishers.bitcaster_event_signal.send",
        side_effect=RuntimeError("queue failed"),
    )

    publish_email_notification(
        "test.email.sent",
        EmailPayload(
            recipients=["user@example.org"],
            context={"title": "Subject"},
        ),
    )


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
        correlation_id="1",
    )

    mock_delay.assert_not_called()


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
def test_handle_bitcaster_event_queues_allowed_event(mocker: Any) -> None:
    mock_delay = mocker.patch("hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay")
    payload = {"recipients": ["user@example.org"]}

    handle_bitcaster_event(
        sender=None,
        event_name="payment.payment_plan.sent_for_approval",
        payload=payload,
        correlation_id="event:1",
    )

    mock_delay.assert_called_once_with("payment.payment_plan.sent_for_approval", payload, "event:1")


def test_send_bitcaster_event_task_passes_options_and_correlation_id(mocker: Any) -> None:
    payload = {
        "options": {"limit_to": ["approver@example.org"]},
    }
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=True)
    backend = SimpleNamespace(is_configured=True, trigger_event=mocker.Mock(return_value=True))
    mocker.patch(
        "hope.apps.core.notifications.tasks.get_notification_backend",
        return_value=backend,
    )

    send_bitcaster_event_task(
        "payment.payment_plan.sent_for_approval",
        payload,
        "payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL",
    )

    backend.trigger_event.assert_called_once_with(
        "payment.payment_plan.sent_for_approval",
        payload,
        options={"limit_to": ["approver@example.org"]},
        cid="payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL",
    )


def test_send_bitcaster_event_task_skips_when_flag_disabled(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=False)
    mock_backend = mocker.patch("hope.apps.core.notifications.tasks.get_notification_backend")

    send_bitcaster_event_task("payment.payment_plan.sent_for_approval", {}, "1")

    mock_backend.assert_not_called()


def test_send_bitcaster_event_task_skips_when_backend_not_configured(mocker: Any) -> None:
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=True)
    backend = SimpleNamespace(is_configured=False, trigger_event=mocker.Mock())
    mocker.patch(
        "hope.apps.core.notifications.tasks.get_notification_backend",
        return_value=backend,
    )

    send_bitcaster_event_task("payment.payment_plan.sent_for_approval", {}, "1")

    backend.trigger_event.assert_not_called()


def test_send_bitcaster_event_task_retries_when_backend_returns_false(mocker: Any) -> None:
    payload = {"options": {}}
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=True)
    backend = SimpleNamespace(is_configured=True, trigger_event=mocker.Mock(return_value=False))
    mocker.patch(
        "hope.apps.core.notifications.tasks.get_notification_backend",
        return_value=backend,
    )
    mock_retry = mocker.patch.object(send_bitcaster_event_task, "retry", side_effect=Retry())

    with pytest.raises(Retry):
        send_bitcaster_event_task(
            "payment.payment_plan.sent_for_approval",
            payload,
            "payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL",
        )

    mock_retry.assert_called_once()
    assert isinstance(mock_retry.call_args.kwargs["exc"], RuntimeError)


def test_send_bitcaster_event_task_retries_unexpected_exception(mocker: Any) -> None:
    payload = {"options": {}}
    mocker.patch("hope.apps.core.notifications.tasks.bitcaster_enabled", return_value=True)
    backend = SimpleNamespace(is_configured=True, trigger_event=mocker.Mock(side_effect=RuntimeError("boom")))
    mocker.patch(
        "hope.apps.core.notifications.tasks.get_notification_backend",
        return_value=backend,
    )
    mock_retry = mocker.patch.object(send_bitcaster_event_task, "retry", side_effect=Retry())

    with pytest.raises(Retry):
        send_bitcaster_event_task(
            "payment.payment_plan.sent_for_approval",
            payload,
            "payment.payment_plan.sent_for_approval:1:SEND_FOR_APPROVAL",
        )

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
