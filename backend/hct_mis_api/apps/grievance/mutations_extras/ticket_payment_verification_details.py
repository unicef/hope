import logging

import graphene
from graphql import GraphQLError

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.utils.exceptions import log_and_raise

logger = logging.getLogger(__name__)


class TicketPaymentVerificationDetailsExtras(graphene.InputObjectType):
    new_received_amount = graphene.Float()
    new_status = graphene.String()


def update_ticket_payment_verification_details_extras(root, info, input, grievance_ticket, extras, **kwargs):
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
