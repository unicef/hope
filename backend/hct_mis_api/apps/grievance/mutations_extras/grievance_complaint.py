from typing import Any, Dict, List

import graphene
from django.contrib.admin.options import get_content_type_for_model

from hct_mis_api.apps.core.utils import decode_and_get_object, decode_id_string, decode_and_get_payment_object
from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketComplaintDetails
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode
from hct_mis_api.apps.payment.models import PaymentRecord, Payment


class GrievanceComplaintTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)
    payment_record = graphene.List(graphene.ID)


def save_grievance_complaint_extras(
    root: Any, info: Any, input: Dict, grievance_ticket: GrievanceTicket, extras: Dict, **kwargs: Any
) -> List[GrievanceTicket]:
    grievance_complaint_extras = extras.get("category", {})
    grievance_complaint_category_extras = grievance_complaint_extras.get("grievance_complaint_ticket_extras", {})

    individual_encoded_id = grievance_complaint_category_extras.get("individual")
    individual = decode_and_get_object(individual_encoded_id, Individual, False)

    household_encoded_id = grievance_complaint_category_extras.get("household")
    household = decode_and_get_object(household_encoded_id, Household, False)

    payment_record_encoded_ids_list = grievance_complaint_category_extras.get("payment_record") or []

    payment_record = None
    if payment_record_encoded_ids_list:
        payment_record_encoded_id = payment_record_encoded_ids_list.pop(0)
        payment_record = decode_and_get_payment_object(payment_record_encoded_id, False)

    TicketComplaintDetails.objects.create(
        individual=individual,
        household=household,
        payment_content_type=get_content_type_for_model(payment_record),
        payment_object_id=payment_record.pk,
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

        TicketComplaintDetails.objects.create(
            individual=individual,
            household=household,
            payment_record=payment_record,
            ticket=ticket,
        )

        ticket.refresh_from_db()
        grievance_tickets_to_return.append(ticket)

    return grievance_tickets_to_return
