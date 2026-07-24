from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Any
from uuid import UUID

from celery.exceptions import Retry
from constance.test import override_config
from django.test import override_settings
import pytest

from hope.apps.accountability.events import survey_sample_xlsx_generated
from hope.apps.core.notifications.bitcaster_client import BitcasterClient, BitcasterClientConfig
from hope.apps.core.notifications.flags import bitcaster_enabled
from hope.apps.core.notifications.notifier import NotificationBackend, get_notification_backend
from hope.apps.core.notifications.payloads import EmailPayload
from hope.apps.core.notifications.tasks import send_bitcaster_event_task
from hope.apps.grievance.events import grievance_assignment_changed
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.payment.events import payment_plan_approved
from hope.apps.periodic_data_update.events import pdu_online_edit_approved
from hope.models import PaymentPlan, PDUOnlineEdit, Survey

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


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
def test_email_event_handler_serializes_payload_and_queues_event(mocker: Any) -> None:
    mock_delay = mocker.patch("hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay")

    class UnknownContextValue:
        def __str__(self) -> str:
            return "unknown-context-value"

    survey_sample_xlsx_generated.send(
        sender=Survey,
        payload=EmailPayload(
            recipients=["user@example.org"],
            cc=["cc@example.org"],
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
        correlation_id="survey-sample:1",
    )

    event_name, payload, correlation_id = mock_delay.call_args.args
    assert event_name == "accountability.survey_sample.xlsx_generated"
    assert correlation_id == "survey-sample:1"
    assert payload["recipients"] == ["user@example.org"]
    assert payload["cc"] == ["cc@example.org"]
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


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
def test_email_event_handler_generates_correlation_id(mocker: Any) -> None:
    mock_delay = mocker.patch("hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay")

    survey_sample_xlsx_generated.send(
        sender=Survey,
        payload=EmailPayload(
            recipients=["user@example.org"],
            context={"title": "Subject"},
        ),
    )

    assert mock_delay.call_args.args[2].startswith("accountability.survey_sample.xlsx_generated:user@example.org:")


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
def test_email_event_handler_swallows_queue_error(mocker: Any) -> None:
    mocker.patch(
        "hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay",
        side_effect=RuntimeError("queue failed"),
    )

    survey_sample_xlsx_generated.send(
        sender=Survey,
        payload=EmailPayload(
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

    survey_sample_xlsx_generated.send(
        sender=Survey,
        payload=EmailPayload(recipients=["user@example.org"], context={}),
        correlation_id="1",
    )

    mock_delay.assert_not_called()


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
@override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
def test_handle_bitcaster_event_queues_allowed_event(mocker: Any) -> None:
    mock_delay = mocker.patch("hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay")
    notification_class = mocker.patch("hope.apps.payment.notifications.PaymentNotification")
    notification = notification_class.return_value
    notification.email.recipients = ["user@example.org"]
    notification.email.variables = {"payment_plan_id": "PP-1"}
    notification.email.ccs = ["actor@example.org"]
    payment_plan = SimpleNamespace(
        id=1,
        business_area=SimpleNamespace(enable_email_notification=True),
    )
    actor = SimpleNamespace()

    payment_plan_approved.send(
        sender=PaymentPlan,
        instance=payment_plan,
        actor=actor,
        action_date="1 January 2025",
    )

    notification_class.assert_called_once_with(payment_plan, "APPROVE", actor, "1 January 2025")
    mock_delay.assert_called_once_with(
        "payment.payment_plan.approved",
        {
            "recipients": ["user@example.org"],
            "context": {"payment_plan_id": "PP-1"},
            "cc": ["actor@example.org"],
        },
        "payment-plan:1:APPROVE",
    )


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
@override_config(SEND_PDU_ONLINE_EDIT_NOTIFICATION=True)
def test_pdu_online_edit_event_handler_queues_allowed_event(mocker: Any) -> None:
    mock_delay = mocker.patch("hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay")
    notification_class = mocker.patch("hope.apps.periodic_data_update.notifications.PDUOnlineEditNotification")
    notification = notification_class.return_value
    notification.email.recipients = ["merger@example.org"]
    notification.email.variables = {"pdu_online_edit_id": "PDU-1"}
    notification.email.ccs = ["actor@example.org"]
    pdu_online_edit = SimpleNamespace(
        id=1,
        business_area=SimpleNamespace(enable_email_notification=True),
    )
    actor = SimpleNamespace()

    pdu_online_edit_approved.send(
        sender=PDUOnlineEdit,
        instance=pdu_online_edit,
        actor=actor,
        action_date="1 January 2025",
    )

    notification_class.assert_called_once_with(pdu_online_edit, "APPROVE", actor, "1 January 2025")
    mock_delay.assert_called_once_with(
        "pdu.online_edit.approved",
        {
            "recipients": ["merger@example.org"],
            "context": {"pdu_online_edit_id": "PDU-1"},
            "cc": ["actor@example.org"],
        },
        "pdu-online-edit:1:APPROVE",
    )


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
def test_email_event_handler_skips_when_business_area_notifications_are_disabled(mocker: Any) -> None:
    mock_delay = mocker.patch("hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay")

    survey_sample_xlsx_generated.send(
        sender=Survey,
        business_area=SimpleNamespace(enable_email_notification=False),
        payload=EmailPayload(recipients=["user@example.org"], context={}),
        correlation_id="1",
    )

    mock_delay.assert_not_called()


@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
@override_config(SEND_GRIEVANCES_NOTIFICATION=True)
def test_grievance_event_handler_prepares_and_queues_notification(mocker: Any) -> None:
    mock_delay = mocker.patch("hope.apps.core.notifications.handlers.send_bitcaster_event_task.delay")
    notification_class = mocker.patch("hope.apps.core.notifications.handlers.GrievanceNotification")
    notification_class.return_value.rendered_email_notifications = [
        (
            EmailPayload(recipients=["user@example.org"], context={"ticket_id": "GRV-1"}),
            "grievance-ticket:1",
        )
    ]
    ticket = SimpleNamespace(
        business_area=SimpleNamespace(enable_email_notification=True),
    )

    grievance_assignment_changed.send(sender=GrievanceTicket, instance=ticket)

    assert notification_class.call_args.args[0] == ticket
    mock_delay.assert_called_once_with(
        "grievance.ticket.assignment_changed",
        {
            "recipients": ["user@example.org"],
            "context": {"ticket_id": "GRV-1"},
            "cc": [],
        },
        "grievance-ticket:1",
    )


@pytest.mark.parametrize(
    ("app_enabled", "business_area_enabled"),
    [(False, True), (True, False)],
)
@override_settings(FLAGS={"BITCASTER_ENABLED": [{"condition": "boolean", "value": True}]})
def test_grievance_event_handler_respects_notification_flags(
    mocker: Any,
    app_enabled: bool,
    business_area_enabled: bool,
) -> None:
    notification_class = mocker.patch("hope.apps.core.notifications.handlers.GrievanceNotification")
    ticket = SimpleNamespace(
        business_area=SimpleNamespace(enable_email_notification=business_area_enabled),
    )

    with override_config(SEND_GRIEVANCES_NOTIFICATION=app_enabled):
        grievance_assignment_changed.send(sender=GrievanceTicket, instance=ticket)

    notification_class.assert_not_called()


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
