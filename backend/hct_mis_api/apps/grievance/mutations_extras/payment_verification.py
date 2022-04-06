import graphene

from django.utils import timezone


class PaymentVerificationTicketExtras(graphene.InputObjectType):
    pass


def save_payment_verification_extras(root, info, input, grievance_ticket, extras, **kwargs):
    payment_verification_details = grievance_ticket.payment_verification_ticket_details
    payment_verification = payment_verification_details.payment_verification
    if not (payment_verification_details.approved and payment_verification and not payment_verification_details.is_multiple_payment_verifications):
        return
    payment_verification.status = payment_verification_details.new_status
    payment_verification.status_date = timezone.now()
    payment_verification.received_amount = payment_verification_details.new_received_amount

    payment_verification.save()
