from typing import TYPE_CHECKING, Any

from django.utils import timezone

import graphene

from hct_mis_api.apps.payment.utils import from_received_to_status, calculate_counts

if TYPE_CHECKING:
    from hct_mis_api.apps.grievance.models import GrievanceTicket


class PaymentVerificationTicketExtras(graphene.InputObjectType):
    pass


def save_payment_verification_extras(grievance_ticket: "GrievanceTicket", info: Any) -> None:
    payment_verification_details = grievance_ticket.payment_verification_ticket_details
    payment_verification = payment_verification_details.payment_verification
    if not (
        payment_verification_details.approve_status
        and payment_verification
        and not payment_verification_details.has_multiple_payment_verifications
    ):
        return

    # TODO: check if status is NOT_RECEIVED
    # update PaymentVerification status
    if payment_verification.payment_obj:

        payment_verification.status = from_received_to_status(
            payment_verification_details.new_received_amount > 0,
            payment_verification_details.new_received_amount,
            payment_verification.payment_obj.delivered_quantity
        )
        payment_verification.status_date = timezone.now()
        payment_verification.received_amount = payment_verification_details.new_received_amount
        payment_verification.save()

        calculate_counts(payment_verification.payment_verification_plan)
        payment_verification.payment_verification_plan.save()
