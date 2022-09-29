import graphene

from hct_mis_api.apps.core.utils import decode_and_get_object
from hct_mis_api.apps.grievance.models import TicketSensitiveDetails
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode
from hct_mis_api.apps.payment.models import PaymentRecord


class SensitiveGrievanceTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)
    payment_record = graphene.List(graphene.ID)


def save_sensitive_grievance_extras(root, info, input, grievance_ticket, extras, **kwargs):
    sensitive_grievance_extras = extras.get("category", {})
    sensitive_grievance_complaint_category_extras = sensitive_grievance_extras.get(
        "sensitive_grievance_ticket_extras", {}
    )

    individual_encoded_id = sensitive_grievance_complaint_category_extras.get("individual")
    individual = decode_and_get_object(individual_encoded_id, Individual, False)

    household_encoded_id = sensitive_grievance_complaint_category_extras.get("household")
    household = decode_and_get_object(household_encoded_id, Household, False)

    payment_record_encoded_ids_list = sensitive_grievance_complaint_category_extras.get("payment_record") or []

    payment_record = None
    if payment_record_encoded_ids_list:
        payment_record_encoded_id = payment_record_encoded_ids_list.pop(0)
        payment_record = decode_and_get_object(payment_record_encoded_id, PaymentRecord, False)

    TicketSensitiveDetails.objects.create(
        individual=individual,
        household=household,
        payment_record=payment_record,
        ticket=grievance_ticket,
    )
    grievance_ticket.refresh_from_db()
    grievance_tickets_to_return = [grievance_ticket]

    for payment_record_encoded_id in payment_record_encoded_ids_list:
        payment_record = decode_and_get_object(payment_record_encoded_id, PaymentRecord, False)

        # copy GrievanceTicket object and assign linked tickets
        ticket = grievance_ticket
        linked_tickets = grievance_ticket.linked_tickets.all()
        ticket.pk = None
        ticket.save()
        ticket.linked_tickets.set(linked_tickets)

        TicketSensitiveDetails.objects.create(
            individual=individual,
            household=household,
            payment_record=payment_record,
            ticket=ticket,
        )

        ticket.refresh_from_db()
        grievance_tickets_to_return.append(ticket)

    return grievance_tickets_to_return
