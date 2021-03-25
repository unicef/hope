def create_grievance_ticket_with_details(main_individual, possible_duplicate, business_area):
    from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails

    details_already_exists = (
        TicketNeedsAdjudicationDetails.objects.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
        .filter(
            golden_records_individual__in=(main_individual, possible_duplicate),
            possible_duplicate__in=(main_individual, possible_duplicate),
        )
        .exists()
    )

    if details_already_exists is True:
        return None, None

    ticket = GrievanceTicket.objects.create(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        business_area=business_area,
    )
    ticket_details = TicketNeedsAdjudicationDetails.objects.create(
        ticket=ticket,
        golden_records_individual=main_individual,
        possible_duplicate=possible_duplicate,
        selected_individual=None,
    )

    return ticket, ticket_details


def create_needs_adjudication_tickets(individuals_queryset, results_key, business_area):
    from hct_mis_api.apps.household.models import Individual

    ticket_details_to_create = []
    for possible_duplicate in individuals_queryset:
        linked_tickets = []
        for individual in possible_duplicate.deduplication_golden_record_results[results_key]:
            ticket, ticket_details = create_grievance_ticket_with_details(
                main_individual=Individual.objects.get(id=individual.get("hit_id")),
                possible_duplicate=possible_duplicate,
                business_area=business_area,
            )
            if ticket is not None and ticket_details is not None:
                linked_tickets.append(ticket)
                ticket_details_to_create.append(ticket_details)

        for ticket in linked_tickets:
            ticket.linked_tickets.set([t for t in linked_tickets if t != ticket])

    return ticket_details_to_create
