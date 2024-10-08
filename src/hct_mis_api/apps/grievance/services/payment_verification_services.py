from typing import Any, Dict, List

from django.utils import timezone

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.payment.models import PaymentVerification
from hct_mis_api.apps.payment.utils import calculate_counts
from hct_mis_api.apps.utils.exceptions import log_and_raise


def update_payment_verification_service(
    grievance_ticket: GrievanceTicket, *args: Any, **kwargs: Any
) -> List[GrievanceTicket]:
    payment_verification_details = grievance_ticket.payment_verification_ticket_details
    payment_verification = payment_verification_details.payment_verification
    if not (
        payment_verification_details.approve_status
        and payment_verification
        and not payment_verification_details.has_multiple_payment_verifications
    ):
        return [grievance_ticket]

    if payment_verification_details.new_status == PaymentVerification.STATUS_NOT_RECEIVED:
        status = payment_verification_details.new_status
    elif (
        payment_verification.payment_obj
        and payment_verification_details.new_received_amount == payment_verification.payment_obj.delivered_quantity
    ):
        status = PaymentVerification.STATUS_RECEIVED
    else:
        status = PaymentVerification.STATUS_RECEIVED_WITH_ISSUES

    payment_verification.status = status
    payment_verification.status_date = timezone.now()
    payment_verification.received_amount = payment_verification_details.new_received_amount
    payment_verification.save()

    calculate_counts(payment_verification.payment_verification_plan)
    payment_verification.payment_verification_plan.save()
    return [grievance_ticket]


def update_ticket_payment_verification_service(
    grievance_ticket: GrievanceTicket, extras: Dict, input_data: Dict
) -> GrievanceTicket:
    if grievance_ticket.status != GrievanceTicket.STATUS_IN_PROGRESS:
        log_and_raise("Payment Details is editable only for Grievance Ticket on status In Progress")

    data = extras.get("ticket_payment_verification_details_extras", {})
    new_received_amount = data.get("new_received_amount")
    new_status = data.get("new_status")

    payment_details = grievance_ticket.payment_verification_ticket_details
    if not payment_details.has_multiple_payment_verifications:
        if new_received_amount:
            payment_details.new_received_amount = new_received_amount
        if new_status:
            payment_details.new_status = new_status

        payment_details.save()
    return grievance_ticket
