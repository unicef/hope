from dataclasses import asdict
from functools import partial
import hashlib
import json
import logging
from typing import Any

from constance import config
from django.core.serializers.json import DjangoJSONEncoder
from django.dispatch import receiver

from hope.api.events import api_credential_created, api_credential_info_requested, api_credential_updated
from hope.apps.accountability.events import survey_sample_xlsx_generated
from hope.apps.core.notifications.events import (
    ACCOUNTABILITY_SURVEY_SAMPLE_XLSX_GENERATED,
    API_CREDENTIAL_CREATED,
    API_CREDENTIAL_INFO_SENT,
    API_CREDENTIAL_UPDATED,
    GRIEVANCE_ASSIGNMENT_CHANGED,
    GRIEVANCE_DEDUPLICATION_CREATED,
    GRIEVANCE_NOTES_ADDED,
    GRIEVANCE_OVERDUE,
    GRIEVANCE_PAYMENT_VERIFICATION_CREATED,
    GRIEVANCE_SEND_BACK_TO_IN_PROGRESS,
    GRIEVANCE_SEND_TO_APPROVAL,
    GRIEVANCE_SENSITIVE_CREATED,
    GRIEVANCE_SENSITIVE_REMINDER,
    GRIEVANCE_SYSTEM_FLAGGING_CREATED,
    PAYMENT_PLAN_APPROVED,
    PAYMENT_PLAN_AUTHORIZED,
    PAYMENT_PLAN_DELIVERY_PASSWORDS_SENT,
    PAYMENT_PLAN_GROUP_PAYMENT_LIST_XLSX_GENERATED,
    PAYMENT_PLAN_PAYMENT_LIST_PDF_GENERATED,
    PAYMENT_PLAN_PAYMENT_LIST_XLSX_GENERATED,
    PAYMENT_PLAN_RECONCILIATION_OVERDUE,
    PAYMENT_PLAN_RELEASED,
    PAYMENT_PLAN_SENT_FOR_APPROVAL,
    PAYMENT_VERIFICATION_PLAN_XLSX_GENERATED,
    PAYMENT_WESTERN_UNION_REPORT_GENERATED,
    PDU_ONLINE_EDIT_APPROVED,
    PDU_ONLINE_EDIT_SENT_BACK,
    PDU_ONLINE_EDIT_SENT_FOR_APPROVAL,
    SANCTION_LIST_CHECK_RESULTS_GENERATED,
)
from hope.apps.core.notifications.flags import bitcaster_enabled
from hope.apps.core.notifications.payloads import EmailPayload
from hope.apps.core.notifications.tasks import send_bitcaster_event_task
from hope.apps.grievance.events import (
    grievance_assignment_changed,
    grievance_deduplication_created,
    grievance_notes_added,
    grievance_overdue,
    grievance_payment_verification_created,
    grievance_sensitive_created,
    grievance_sensitive_overdue,
    grievance_sent_back_to_in_progress,
    grievance_sent_to_approval,
    grievance_system_flagging_created,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification
from hope.apps.payment.events import (
    payment_delivery_export_passwords_generated,
    payment_plan_approved,
    payment_plan_authorized,
    payment_plan_group_payment_list_xlsx_generated,
    payment_plan_payment_list_pdf_generated,
    payment_plan_payment_list_xlsx_generated,
    payment_plan_reconciliation_overdue,
    payment_plan_released,
    payment_plan_sent_for_approval,
    payment_verification_plan_xlsx_generated,
    western_union_report_generated,
)
from hope.apps.periodic_data_update.events import (
    pdu_online_edit_approved,
    pdu_online_edit_sent_back,
    pdu_online_edit_sent_for_approval,
)
from hope.apps.sanction_list.events import sanction_list_check_results_generated
from hope.models import (
    APIToken,
    BusinessArea,
    FileTemp,
    PaymentPlan,
    PaymentPlanGroup,
    PaymentVerificationPlan,
    PDUOnlineEdit,
    Survey,
    UploadedXLSXFile,
    WesternUnionPaymentPlanReport,
)

logger = logging.getLogger(__name__)


def _email_notifications_enabled(
    business_area: BusinessArea | None = None,
    application_enabled: bool = True,
) -> bool:
    return (
        bitcaster_enabled()
        and application_enabled
        and (business_area is None or business_area.enable_email_notification)
    )


def _handle_email_event(
    event_name: str,
    payload: EmailPayload,
    correlation_id: str | None = None,
    *,
    business_area: BusinessArea | None = None,
    application_enabled: bool = True,
) -> None:
    if not _email_notifications_enabled(business_area, application_enabled):
        logger.debug("Skipping Bitcaster event '%s': notifications disabled.", event_name)
        return

    try:
        serialized_payload = _json_safe_context(asdict(payload))
        correlation_id = correlation_id or _build_email_correlation_id(event_name, payload)
        send_bitcaster_event_task.delay(event_name, serialized_payload, correlation_id)
    except Exception:
        logger.exception("Failed to queue Bitcaster event '%s'.", event_name)


def _handle_event(
    event_name: str,
    sender: Any,
    payload: EmailPayload,
    correlation_id: str | None = None,
    business_area: BusinessArea | None = None,
    **kwargs: Any,
) -> None:
    _handle_email_event(event_name, payload, correlation_id, business_area=business_area)


def _handle_notifications(
    event_name: str,
    sender: Any,
    notifications: list[tuple[EmailPayload, str]],
    **kwargs: Any,
) -> None:
    for payload, correlation_id in notifications:
        _handle_email_event(event_name, payload, correlation_id)


def _handle_grievance_event(
    action: Any,
    event_name: str,
    signal: Any,
    sender: type[GrievanceTicket],
    instance: GrievanceTicket,
    **kwargs: Any,
) -> None:
    if not _email_notifications_enabled(instance.business_area, config.SEND_GRIEVANCES_NOTIFICATION):
        return

    notification = GrievanceNotification(instance, action, **kwargs)
    _handle_notifications(event_name, sender, notification.rendered_email_notifications)


def _connect(signal: Any, sender: type[Any], event_name: str, handler: Any = _handle_event) -> None:
    signal.connect(
        partial(handler, event_name),
        sender=sender,
        weak=False,
        dispatch_uid=f"bitcaster:{event_name}",
    )


def _json_safe_context(context: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(context, cls=DjangoJSONEncoder, default=str))


def _build_email_correlation_id(event_name: str, payload: EmailPayload) -> str:
    source = json.dumps(
        {
            "event_name": event_name,
            "recipients": payload.recipients,
            "context": _json_safe_context(payload.context),
            "cc": payload.cc,
        },
        sort_keys=True,
    )
    digest = hashlib.sha256(source.encode()).hexdigest()[:16]
    return f"{event_name}:{':'.join(payload.recipients)}:{digest}"


PAYMENT_PLAN_WORKFLOW_EVENTS = {
    payment_plan_sent_for_approval: (PAYMENT_PLAN_SENT_FOR_APPROVAL, PaymentPlan.Action.SEND_FOR_APPROVAL.value),
    payment_plan_approved: (PAYMENT_PLAN_APPROVED, PaymentPlan.Action.APPROVE.value),
    payment_plan_authorized: (PAYMENT_PLAN_AUTHORIZED, PaymentPlan.Action.AUTHORIZE.value),
    payment_plan_released: (PAYMENT_PLAN_RELEASED, PaymentPlan.Action.REVIEW.value),
}


@receiver(tuple(PAYMENT_PLAN_WORKFLOW_EVENTS), sender=PaymentPlan)
def handle_payment_plan_workflow_event(
    signal: Any,
    sender: type[PaymentPlan],
    instance: PaymentPlan,
    actor: Any,
    action_date: str,
    **kwargs: Any,
) -> None:
    if not _email_notifications_enabled(instance.business_area, config.SEND_PAYMENT_PLANS_NOTIFICATION):
        return

    from hope.apps.payment.notifications import PaymentNotification

    event_name, action = PAYMENT_PLAN_WORKFLOW_EVENTS[signal]
    notification = PaymentNotification(instance, action, actor, action_date)
    _handle_email_event(
        event_name,
        EmailPayload(
            recipients=notification.email.recipients,
            context=notification.email.variables or {},
            cc=notification.email.ccs,
        ),
        f"payment-plan:{instance.id}:{action}",
    )


PDU_ONLINE_EDIT_WORKFLOW_EVENTS = {
    pdu_online_edit_sent_for_approval: (PDU_ONLINE_EDIT_SENT_FOR_APPROVAL, "SEND_FOR_APPROVAL"),
    pdu_online_edit_approved: (PDU_ONLINE_EDIT_APPROVED, "APPROVE"),
    pdu_online_edit_sent_back: (PDU_ONLINE_EDIT_SENT_BACK, "SEND_BACK"),
}


@receiver(tuple(PDU_ONLINE_EDIT_WORKFLOW_EVENTS), sender=PDUOnlineEdit)
def handle_pdu_online_edit_workflow_event(
    signal: Any,
    sender: type[PDUOnlineEdit],
    instance: PDUOnlineEdit,
    actor: Any,
    action_date: str,
    **kwargs: Any,
) -> None:
    if not _email_notifications_enabled(instance.business_area, config.SEND_PDU_ONLINE_EDIT_NOTIFICATION):
        return

    from hope.apps.periodic_data_update.notifications import PDUOnlineEditNotification

    event_name, action = PDU_ONLINE_EDIT_WORKFLOW_EVENTS[signal]
    notification = PDUOnlineEditNotification(instance, action, actor, action_date)
    _handle_email_event(
        event_name,
        EmailPayload(
            recipients=notification.email.recipients,
            context=notification.email.variables or {},
            cc=notification.email.ccs,
        ),
        f"pdu-online-edit:{instance.id}:{action}",
    )


_connect(survey_sample_xlsx_generated, Survey, ACCOUNTABILITY_SURVEY_SAMPLE_XLSX_GENERATED)
_connect(api_credential_info_requested, APIToken, API_CREDENTIAL_INFO_SENT)
_connect(api_credential_created, APIToken, API_CREDENTIAL_CREATED)
_connect(api_credential_updated, APIToken, API_CREDENTIAL_UPDATED)
_connect(payment_plan_payment_list_xlsx_generated, PaymentPlan, PAYMENT_PLAN_PAYMENT_LIST_XLSX_GENERATED)
_connect(payment_plan_payment_list_pdf_generated, PaymentPlan, PAYMENT_PLAN_PAYMENT_LIST_PDF_GENERATED)
_connect(
    payment_plan_group_payment_list_xlsx_generated,
    PaymentPlanGroup,
    PAYMENT_PLAN_GROUP_PAYMENT_LIST_XLSX_GENERATED,
)
_connect(
    payment_verification_plan_xlsx_generated,
    PaymentVerificationPlan,
    PAYMENT_VERIFICATION_PLAN_XLSX_GENERATED,
)
_connect(payment_delivery_export_passwords_generated, FileTemp, PAYMENT_PLAN_DELIVERY_PASSWORDS_SENT)
_connect(payment_plan_reconciliation_overdue, PaymentPlan, PAYMENT_PLAN_RECONCILIATION_OVERDUE)
_connect(western_union_report_generated, WesternUnionPaymentPlanReport, PAYMENT_WESTERN_UNION_REPORT_GENERATED)
_connect(sanction_list_check_results_generated, UploadedXLSXFile, SANCTION_LIST_CHECK_RESULTS_GENERATED)

_connect(
    grievance_assignment_changed,
    GrievanceTicket,
    GRIEVANCE_ASSIGNMENT_CHANGED,
    partial(_handle_grievance_event, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED),
)
_connect(
    grievance_system_flagging_created,
    GrievanceTicket,
    GRIEVANCE_SYSTEM_FLAGGING_CREATED,
    partial(_handle_grievance_event, GrievanceNotification.ACTION_SYSTEM_FLAGGING_CREATED),
)
_connect(
    grievance_deduplication_created,
    GrievanceTicket,
    GRIEVANCE_DEDUPLICATION_CREATED,
    partial(_handle_grievance_event, GrievanceNotification.ACTION_DEDUPLICATION_CREATED),
)
_connect(
    grievance_payment_verification_created,
    GrievanceTicket,
    GRIEVANCE_PAYMENT_VERIFICATION_CREATED,
    partial(_handle_grievance_event, GrievanceNotification.ACTION_PAYMENT_VERIFICATION_CREATED),
)
_connect(
    grievance_notes_added,
    GrievanceTicket,
    GRIEVANCE_NOTES_ADDED,
    partial(_handle_grievance_event, GrievanceNotification.ACTION_NOTES_ADDED),
)
_connect(
    grievance_sent_back_to_in_progress,
    GrievanceTicket,
    GRIEVANCE_SEND_BACK_TO_IN_PROGRESS,
    partial(_handle_grievance_event, GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS),
)
_connect(
    grievance_sent_to_approval,
    GrievanceTicket,
    GRIEVANCE_SEND_TO_APPROVAL,
    partial(_handle_grievance_event, GrievanceNotification.ACTION_SEND_TO_APPROVAL),
)
_connect(
    grievance_sensitive_created,
    GrievanceTicket,
    GRIEVANCE_SENSITIVE_CREATED,
    partial(_handle_grievance_event, GrievanceNotification.ACTION_SENSITIVE_CREATED),
)
_connect(
    grievance_sensitive_overdue,
    GrievanceTicket,
    GRIEVANCE_SENSITIVE_REMINDER,
    partial(_handle_grievance_event, GrievanceNotification.ACTION_SENSITIVE_REMINDER),
)
_connect(
    grievance_overdue,
    GrievanceTicket,
    GRIEVANCE_OVERDUE,
    partial(_handle_grievance_event, GrievanceNotification.ACTION_OVERDUE),
)
