from hct_mis_api.apps.grievance.notifications import GrievanceNotification


def create_grievance_ticket_with_details(main_individual, possible_duplicate, business_area, **kwargs):
    from hct_mis_api.apps.grievance.models import (
        GrievanceTicket,
        TicketNeedsAdjudicationDetails,
    )

    details_already_exists = (
        TicketNeedsAdjudicationDetails.objects.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
        .filter(
            golden_records_individual__in=(main_individual, possible_duplicate),
            possible_duplicate__in=(main_individual, possible_duplicate),
        )
        .exists()
    )

    if details_already_exists:
        return None, None

    household = main_individual.household
    admin_level_2 = household.admin2 if household else None
    admin_level_2_new = household.admin2_new if household else None
    area = household.village if household else ""

    ticket = GrievanceTicket.objects.create(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        business_area=business_area,
        admin2=admin_level_2,
        admin2_new=admin_level_2_new,
        area=area,
        registration_data_import=kwargs.pop("registration_data_import", None),
    )
    ticket_details = TicketNeedsAdjudicationDetails.objects.create(
        ticket=ticket,
        golden_records_individual=main_individual,
        possible_duplicate=possible_duplicate,
        is_multiple_duplicates_version=kwargs.get("is_multiple_duplicates_version", False),
        selected_individual=None,
        extra_data={
            "golden_records": main_individual.get_deduplication_golden_record(),
            "possible_duplicate": possible_duplicate.get_deduplication_golden_record(),
        }
    )

    possible_duplicates = kwargs.get("possible_duplicates")
    if possible_duplicates:
        ticket_details.possible_duplicates.add(*possible_duplicates)

    GrievanceNotification.send_all_notifications(
        GrievanceNotification.prepare_notification_for_ticket_creation(ticket)
    )
    return ticket, ticket_details


def create_needs_adjudication_tickets(individuals_queryset, results_key, business_area, **kwargs):
    from hct_mis_api.apps.household.models import Individual

    if not individuals_queryset:
        return

    ticket_details_to_create = []
    unique_individual_sets = []  # checks combination of individuals

    for possible_duplicate in individuals_queryset:
        linked_tickets = []
        possible_duplicates = []

        for individual in possible_duplicate.deduplication_golden_record_results[results_key]:
            duplicate = Individual.objects.filter(id=individual.get("hit_id")).first()

            if not duplicate:
                continue
            possible_duplicates.append(duplicate)

        individuals_set = {possible_duplicate, *possible_duplicates}
        if not possible_duplicates or individuals_set in unique_individual_sets:
            continue

        unique_individual_sets.append(individuals_set)

        ticket, ticket_details = create_grievance_ticket_with_details(
            main_individual=possible_duplicate,
            possible_duplicate=possible_duplicate,  # for backward compatibility
            business_area=business_area,
            registration_data_import=kwargs.pop("registration_data_import", None),
            possible_duplicates=possible_duplicates,
            is_multiple_duplicates_version=True
        )

        if ticket and ticket_details:
            linked_tickets.append(ticket)
            ticket_details_to_create.append(ticket_details)

        for ticket in linked_tickets:
            ticket.linked_tickets.set([t for t in linked_tickets if t != ticket])

    return ticket_details_to_create
