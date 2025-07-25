from django.core.exceptions import ValidationError

from hct_mis_api.apps.grievance.models import GrievanceTicket


def create_tickets_based_on_payment_records_service(
    grievance_ticket: GrievanceTicket, details: dict, model: type
) -> list[GrievanceTicket]:
    individual = details.get("individual")
    household = details.get("household")
    # Payment ids
    payment_records = details.get("payment_record", [])
    grievance_tickets_to_return = []
    # create only one ticket details if no payment ids
    if not payment_records:
        model.objects.create(
            individual=individual,
            household=household,
            payment=None,
            ticket=grievance_ticket,
        )
        grievance_ticket.refresh_from_db()
        grievance_tickets_to_return = [grievance_ticket]

    # for the first ticket_details use already create grievance_ticket
    ticket: GrievanceTicket | None = grievance_ticket
    # create linked tickets for all payment ids
    for payment in payment_records:
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
    grievance_ticket: GrievanceTicket, extras: dict, input_data: dict
) -> GrievanceTicket:
    ticket_details = grievance_ticket.ticket_details

    if household := input_data.get("household"):
        if ticket_details.household and ticket_details.household != household:
            raise ValidationError("Cannot change household")
        ticket_details.household = household

    if individual := input_data.get("individual"):
        if ticket_details.individual and ticket_details.individual != individual:
            raise ValidationError("Cannot change individual")
        ticket_details.individual = individual

    if payment := input_data.get("payment_record"):
        ticket_details.payment = payment
    ticket_details.save()
    return grievance_ticket
