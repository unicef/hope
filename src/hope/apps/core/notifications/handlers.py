from dataclasses import asdict
from functools import partial
import hashlib
import json
import logging
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder

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


def _handle_event(
    event_name: str,
    sender: Any,
    payload: EmailPayload,
    **kwargs: Any,
) -> None:
    if not bitcaster_enabled():
        logger.debug("Skipping Bitcaster event '%s': integration disabled.", event_name)
        return

    try:
        business_area = kwargs.get("business_area")
        serialized_payload = _json_safe_context(asdict(payload))
        serialized_payload["send_notification"] = kwargs.get("send_notification", True) and (
            business_area is None or business_area.enable_email_notification
        )
        correlation_id = kwargs.get("correlation_id") or _build_email_correlation_id(event_name, payload)
        send_bitcaster_event_task.delay(event_name, serialized_payload, correlation_id)
    except Exception:
        logger.exception("Failed to queue Bitcaster event '%s'.", event_name)


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


_connect(survey_sample_xlsx_generated, Survey, ACCOUNTABILITY_SURVEY_SAMPLE_XLSX_GENERATED)
_connect(api_credential_info_requested, APIToken, API_CREDENTIAL_INFO_SENT)
_connect(api_credential_created, APIToken, API_CREDENTIAL_CREATED)
_connect(api_credential_updated, APIToken, API_CREDENTIAL_UPDATED)
_connect(payment_plan_sent_for_approval, PaymentPlan, PAYMENT_PLAN_SENT_FOR_APPROVAL)
_connect(payment_plan_approved, PaymentPlan, PAYMENT_PLAN_APPROVED)
_connect(payment_plan_authorized, PaymentPlan, PAYMENT_PLAN_AUTHORIZED)
_connect(payment_plan_released, PaymentPlan, PAYMENT_PLAN_RELEASED)
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
_connect(pdu_online_edit_sent_for_approval, PDUOnlineEdit, PDU_ONLINE_EDIT_SENT_FOR_APPROVAL)
_connect(pdu_online_edit_approved, PDUOnlineEdit, PDU_ONLINE_EDIT_APPROVED)
_connect(pdu_online_edit_sent_back, PDUOnlineEdit, PDU_ONLINE_EDIT_SENT_BACK)
_connect(grievance_assignment_changed, GrievanceTicket, GRIEVANCE_ASSIGNMENT_CHANGED)
_connect(grievance_system_flagging_created, GrievanceTicket, GRIEVANCE_SYSTEM_FLAGGING_CREATED)
_connect(grievance_deduplication_created, GrievanceTicket, GRIEVANCE_DEDUPLICATION_CREATED)
_connect(grievance_payment_verification_created, GrievanceTicket, GRIEVANCE_PAYMENT_VERIFICATION_CREATED)
_connect(grievance_notes_added, GrievanceTicket, GRIEVANCE_NOTES_ADDED)
_connect(grievance_sent_back_to_in_progress, GrievanceTicket, GRIEVANCE_SEND_BACK_TO_IN_PROGRESS)
_connect(grievance_sent_to_approval, GrievanceTicket, GRIEVANCE_SEND_TO_APPROVAL)
_connect(grievance_sensitive_created, GrievanceTicket, GRIEVANCE_SENSITIVE_CREATED)
_connect(grievance_sensitive_overdue, GrievanceTicket, GRIEVANCE_SENSITIVE_REMINDER)
_connect(grievance_overdue, GrievanceTicket, GRIEVANCE_OVERDUE)
