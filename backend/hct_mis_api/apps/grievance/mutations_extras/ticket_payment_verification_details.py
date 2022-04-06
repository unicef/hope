import graphene

from hct_mis_api.apps.payment.models import PaymentVerification


class TicketPaymentVerificationDetailsExtras(graphene.InputObjectType):
    new_received_amount = graphene.Float()
    approved_new_received_amount = graphene.Boolean()


def update_ticket_payment_verification_details_extras(root, info, input, grievance_ticket, extras, **kwargs):
    data = extras.get("ticket_payment_verification_details_extras", {})
    new_received_amount = data.get("new_received_amount")
    approved_new_received_amount = data.get("approved_new_received_amount")

    ticket_details = grievance_ticket.payment_verification_ticket_details
    if not ticket_details.is_multiple_payment_verifications:
        if new_received_amount:
            ticket_details.new_received_amount = new_received_amount
            # update status if payment_verification not null
            if ticket_details.payment_verification and ticket_details.payment_verification.payment_record:
                if new_received_amount >= ticket_details.payment_verification.payment_record.delivered_quantity:
                    ticket_details.new_status = PaymentVerification.STATUS_RECEIVED
                else:
                    ticket_details.new_status = PaymentVerification.STATUS_RECEIVED_WITH_ISSUES

        if approved_new_received_amount:
            ticket_details.approved = True

        ticket_details.save()
