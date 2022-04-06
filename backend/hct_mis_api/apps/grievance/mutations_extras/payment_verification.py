import graphene

from django.utils import timezone


class PaymentVerificationTicketExtras(graphene.InputObjectType):
    pass


def save_payment_verification_extras(root, info, input, grievance_ticket, extras, **kwargs):

    ticket_details = grievance_ticket.payment_verification_ticket_details
    if ticket_details.approved and ticket_details.payment_verification and not ticket_details.is_multiple_payment_verifications:
        ticket_details.payment_verification.status = ticket_details.new_status
        ticket_details.payment_verification.status_date = timezone.now()
        ticket_details.payment_verification.received_amount = ticket_details.new_received_amount

        ticket_details.payment_verification.save()
