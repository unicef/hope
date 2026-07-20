# Payment
PAYMENT_PLAN_SENT_FOR_APPROVAL = "payment.payment_plan.sent_for_approval"
PAYMENT_PLAN_APPROVED = "payment.payment_plan.approved"
PAYMENT_PLAN_AUTHORIZED = "payment.payment_plan.authorized"
PAYMENT_PLAN_RELEASED = "payment.payment_plan.released"

PAYMENT_PLAN_ACTION_TO_BITCASTER_EVENT = {
    "SEND_FOR_APPROVAL": PAYMENT_PLAN_SENT_FOR_APPROVAL,
    "APPROVE": PAYMENT_PLAN_APPROVED,
    "AUTHORIZE": PAYMENT_PLAN_AUTHORIZED,
    "REVIEW": PAYMENT_PLAN_RELEASED,
}

PAYMENT_PLAN_PAYMENT_LIST_XLSX_GENERATED = "payment.payment_plan.payment_list_xlsx_generated"
PAYMENT_PLAN_PAYMENT_LIST_PDF_GENERATED = "payment.payment_plan.payment_list_pdf_generated"
PAYMENT_PLAN_GROUP_PAYMENT_LIST_XLSX_GENERATED = "payment.payment_plan_group.payment_list_xlsx_generated"
PAYMENT_VERIFICATION_PLAN_XLSX_GENERATED = "payment.payment_verification_plan.xlsx_generated"
PAYMENT_PLAN_DELIVERY_PASSWORDS_SENT = "payment.payment_plan.delivery_passwords_sent"
PAYMENT_PLAN_RECONCILIATION_OVERDUE = "payment.payment_plan.reconciliation_overdue"
PAYMENT_WESTERN_UNION_REPORT_GENERATED = "payment.western_union_report.generated"


# Periodic Data Update
PDU_ONLINE_EDIT_SENT_FOR_APPROVAL = "pdu.online_edit.sent_for_approval"
PDU_ONLINE_EDIT_APPROVED = "pdu.online_edit.approved"
PDU_ONLINE_EDIT_SENT_BACK = "pdu.online_edit.sent_back"

PDU_ONLINE_EDIT_ACTION_TO_BITCASTER_EVENT = {
    "SEND_FOR_APPROVAL": PDU_ONLINE_EDIT_SENT_FOR_APPROVAL,
    "APPROVE": PDU_ONLINE_EDIT_APPROVED,
    "SEND_BACK": PDU_ONLINE_EDIT_SENT_BACK,
}


# Accountability
ACCOUNTABILITY_SURVEY_SAMPLE_XLSX_GENERATED = "accountability.survey_sample.xlsx_generated"


# API
API_CREDENTIAL_INFO_SENT = "api.api_token.info_sent"
API_CREDENTIAL_CREATED = "api.api_token.created"
API_CREDENTIAL_UPDATED = "api.api_token.updated"

API_TOKEN_ACTION_TO_BITCASTER_EVENT = {
    "info": API_CREDENTIAL_INFO_SENT,
    "created": API_CREDENTIAL_CREATED,
    "updated": API_CREDENTIAL_UPDATED,
}


# Grievance
GRIEVANCE_ASSIGNMENT_CHANGED = "grievance.ticket.assignment_changed"
GRIEVANCE_SYSTEM_FLAGGING_CREATED = "grievance.ticket.system_flagging_created"
GRIEVANCE_DEDUPLICATION_CREATED = "grievance.ticket.deduplication_created"
GRIEVANCE_PAYMENT_VERIFICATION_CREATED = "grievance.ticket.payment_verification_created"
GRIEVANCE_NOTES_ADDED = "grievance.ticket.notes_added"
GRIEVANCE_SEND_BACK_TO_IN_PROGRESS = "grievance.ticket.sent_back_to_in_progress"
GRIEVANCE_SENSITIVE_CREATED = "grievance.ticket.sensitive_created"
GRIEVANCE_SENSITIVE_REMINDER = "grievance.ticket.sensitive_reminder"
GRIEVANCE_OVERDUE = "grievance.ticket.overdue"
GRIEVANCE_SEND_TO_APPROVAL = "grievance.ticket.sent_to_approval"


# Sanction List
SANCTION_LIST_CHECK_RESULTS_GENERATED = "sanction_list.check.results_generated"
