from base64 import b64decode
from typing import Dict, List, Optional, Type

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.core.utils import (
    decode_and_get_object,
    decode_and_get_object_required,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.payment.models import Payment


def create_tickets_based_on_payment_records_service(
    grievance_ticket: GrievanceTicket, details: Dict, model: Type
) -> List[GrievanceTicket]:
    individual_encoded_id = details.get("individual")
    individual = decode_and_get_object(individual_encoded_id, Individual, False)

    household_encoded_id = details.get("household")
    household = decode_and_get_object(household_encoded_id, Household, False)
    # Payment or PaymentRecord ids
    payment_record_encoded_ids_list = details.get("payment_record", [])
    grievance_tickets_to_return = []
    # create only one ticket details if no payment ids
    if not payment_record_encoded_ids_list:
        model.objects.create(
            individual=individual,
            household=household,
            payment=None,
            ticket=grievance_ticket,
        )
        grievance_ticket.refresh_from_db()
        grievance_tickets_to_return = [grievance_ticket]

    # for the first ticket_details use already create grievance_ticket
    ticket: Optional[GrievanceTicket] = grievance_ticket
    # create linked tickets for all payment ids
    for payment_record_encoded_id in payment_record_encoded_ids_list:
        node_name, obj_id = b64decode(payment_record_encoded_id).decode().split(":")

        payment: Payment = get_object_or_404(Payment, id=obj_id)
        # copy GrievanceTicket object and assign linked tickets
        if not ticket:
            ticket = grievance_ticket
            linked_tickets = grievance_ticket.linked_tickets.all()
            programs_ticket = grievance_ticket.programs.all()
            ticket.pk = None
            ticket.save()
            ticket.linked_tickets.set(linked_tickets)
            ticket.programs.set(programs_ticket)

        model.objects.create(
            individual=individual,
            household=household,
            payment=payment,
            ticket=ticket,
        )
        ticket.refresh_from_db()
        grievance_tickets_to_return.append(ticket)
        ticket = None

    return grievance_tickets_to_return


def update_ticket_based_on_payment_record_service(
    grievance_ticket: GrievanceTicket, extras: Dict, input_data: Dict
) -> GrievanceTicket:
    ticket_details = grievance_ticket.ticket_details

    if household_id := input_data.get("household"):
        household = decode_and_get_object_required(household_id, Household)
        if ticket_details.household and ticket_details.household != household:
            raise ValidationError("Cannot change household")
        ticket_details.household = household

    if individual_id := input_data.get("individual"):
        individual = decode_and_get_object_required(individual_id, Individual)
        if ticket_details.individual and ticket_details.individual != individual:
            raise ValidationError("Cannot change individual")
        ticket_details.individual = individual

    if payment_record_id := input_data.get("payment_record"):
        node_name, obj_id = b64decode(payment_record_id).decode().split(":")

        payment_record: "Payment" = get_object_or_404(Payment, id=obj_id)
        ticket_details.payment = payment_record
    ticket_details.save()
    return grievance_ticket
