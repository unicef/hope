import logging

from hct_mis_api.apps.grievance.notifications import GrievanceNotification

logger = logging.getLogger(__name__)


def _get_min_max_score(golden_records):
    items = [item.get("score", 0.0) for item in golden_records]

    return min(items, default=0.0), max(items, default=0.0)


def create_grievance_ticket_with_details(main_individual, possible_duplicate, business_area, **kwargs):
    from hct_mis_api.apps.grievance.models import (
        GrievanceTicket,
        TicketNeedsAdjudicationDetails,
    )

    possible_duplicates = kwargs.get("possible_duplicates")
    if not possible_duplicates:
        return None, None

    registration_data_import = kwargs.get("registration_data_import", None)
    if registration_data_import:
        ticket_details_to_check = TicketNeedsAdjudicationDetails.objects.exclude(
            ticket__status=GrievanceTicket.STATUS_CLOSED
        ).filter(ticket__registration_data_import_id=registration_data_import.pk)

        ticket_all_individuals = {main_individual, *possible_duplicates}

        for ticket_detail in ticket_details_to_check:
            other_ticket_all_individuals = {
                ticket_detail.golden_records_individual,
                *ticket_detail.possible_duplicates.all(),
            }
            if set.intersection(ticket_all_individuals, other_ticket_all_individuals):
                return None, None

    household = main_individual.household
    admin_level_2 = household.admin2 if household else None
    area = household.village if household else ""

    ticket = GrievanceTicket.objects.create(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        business_area=business_area,
        admin2=admin_level_2,
        area=area,
        registration_data_import=registration_data_import,
    )
    golden_records = main_individual.get_deduplication_golden_record()
    extra_data = {
        "golden_records": golden_records,
        "possible_duplicate": possible_duplicate.get_deduplication_golden_record(),
    }
    score_min, score_max = _get_min_max_score(golden_records)
    ticket_details = TicketNeedsAdjudicationDetails.objects.create(
        ticket=ticket,
        golden_records_individual=main_individual,
        possible_duplicate=possible_duplicate,
        is_multiple_duplicates_version=kwargs.get("is_multiple_duplicates_version", False),
        selected_individual=None,
        extra_data=extra_data,
        score_min=score_min,
        score_max=score_max,
    )

    ticket_details.possible_duplicates.add(*possible_duplicates)

    GrievanceNotification.send_all_notifications(GrievanceNotification.prepare_notification_for_ticket_creation(ticket))

    return ticket, ticket_details


def create_needs_adjudication_tickets(individuals_queryset, results_key, business_area, **kwargs):
    from hct_mis_api.apps.household.models import Individual

    if not individuals_queryset:
        return

    ticket_details_to_create = []
    for possible_duplicate in individuals_queryset:
        linked_tickets = []
        possible_duplicates = []

        for individual in possible_duplicate.deduplication_golden_record_results[results_key]:
            duplicate = Individual.objects.filter(id=individual.get("hit_id")).first()
            if not duplicate:
                continue

            possible_duplicates.append(duplicate)

        ticket, ticket_details = create_grievance_ticket_with_details(
            main_individual=possible_duplicate,
            possible_duplicate=possible_duplicate,  # for backward compatibility
            business_area=business_area,
            registration_data_import=kwargs.get("registration_data_import", None),
            possible_duplicates=possible_duplicates,
            is_multiple_duplicates_version=True,
        )

        if ticket and ticket_details:
            linked_tickets.append(ticket)
            ticket_details_to_create.append(ticket_details)

        for ticket in linked_tickets:
            ticket.linked_tickets.set([t for t in linked_tickets if t != ticket])

    return ticket_details_to_create
