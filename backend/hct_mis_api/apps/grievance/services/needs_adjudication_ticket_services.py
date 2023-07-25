from typing import Dict, List, Optional, Sequence, Tuple

from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.grievance.notifications import GrievanceNotification
from hct_mis_api.apps.grievance.services.reassign_roles_services import (
    reassign_roles_on_disable_individual_service,
)
from hct_mis_api.apps.grievance.utils import traverse_sibling_tickets
from hct_mis_api.apps.household.models import (
    UNIQUE,
    UNIQUE_IN_BATCH,
    Household,
    Individual,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import (
    HardDocumentDeduplication,
)


def _clear_deduplication_individuals_fields(individuals: Sequence[Individual]) -> None:
    for individual in individuals:
        individual.deduplication_golden_record_status = UNIQUE
        individual.deduplication_batch_status = UNIQUE_IN_BATCH
        individual.deduplication_golden_record_results = {}
        individual.deduplication_batch_results = {}
        HardDocumentDeduplication().deduplicate(individual.documents.all())
    Individual.objects.bulk_update(
        individuals,
        [
            "deduplication_golden_record_status",
            "deduplication_batch_status",
            "deduplication_golden_record_results",
            "deduplication_batch_results",
        ],
    )


def close_needs_adjudication_old_ticket(ticket_details: TicketNeedsAdjudicationDetails, user: AbstractUser) -> None:
    both_individuals = (ticket_details.golden_records_individual, ticket_details.possible_duplicate)

    if ticket_details.selected_individual is None:
        _clear_deduplication_individuals_fields(both_individuals)
    else:
        individual_to_remove = ticket_details.selected_individual
        unique_individuals = [individual for individual in both_individuals if individual.id != individual_to_remove.id]
        mark_as_duplicate_individual_and_reassign_roles(
            ticket_details, individual_to_remove, user, unique_individuals[0]
        )
        _clear_deduplication_individuals_fields(unique_individuals)


def close_needs_adjudication_new_ticket(ticket_details: TicketNeedsAdjudicationDetails, user: AbstractUser) -> None:
    individuals = (ticket_details.golden_records_individual, *ticket_details.possible_duplicates.all())

    if selected_individuals := ticket_details.selected_individuals.all():
        unique_individuals = [individual for individual in individuals if individual not in selected_individuals]
        for individual_to_remove in selected_individuals:
            mark_as_duplicate_individual_and_reassign_roles(
                ticket_details, individual_to_remove, user, unique_individuals[0]
            )
        _clear_deduplication_individuals_fields(unique_individuals)
    else:
        _clear_deduplication_individuals_fields(individuals)


def close_needs_adjudication_ticket_service(grievance_ticket: GrievanceTicket, user: AbstractUser) -> None:
    ticket_details = grievance_ticket.ticket_details
    if not ticket_details:
        return

    if ticket_details.is_multiple_duplicates_version:
        selected_individuals = ticket_details.selected_individuals.all()
        traverse_sibling_tickets(grievance_ticket, selected_individuals)

        close_needs_adjudication_new_ticket(ticket_details, user)
    else:
        close_needs_adjudication_old_ticket(ticket_details, user)


def _get_min_max_score(golden_records: List[Dict]) -> Tuple[float, float]:
    items = [item.get("score", 0.0) for item in golden_records]

    return min(items, default=0.0), max(items, default=0.0)


def create_grievance_ticket_with_details(
    main_individual: Individual,
    possible_duplicate: Individual,
    business_area: BusinessArea,
    possible_duplicates: Optional[List[Individual]] = None,
    registration_data_import: Optional[RegistrationDataImport] = None,
    is_multiple_duplicates_version: bool = False,
) -> Tuple[Optional[GrievanceTicket], Optional[TicketNeedsAdjudicationDetails]]:
    from hct_mis_api.apps.grievance.models import (
        GrievanceTicket,
        TicketNeedsAdjudicationDetails,
    )

    if not possible_duplicates:
        return None, None

    ticket_all_individuals = {main_individual, *possible_duplicates}

    ticket_already_exists = (
        TicketNeedsAdjudicationDetails.objects.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
        .filter(golden_records_individual__in=ticket_all_individuals, possible_duplicates__in=ticket_all_individuals)
        .exists()
    )

    if ticket_already_exists:
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
        is_multiple_duplicates_version=is_multiple_duplicates_version,
        selected_individual=None,
        extra_data=extra_data,
        score_min=score_min,
        score_max=score_max,
    )

    ticket_details.possible_duplicates.add(*possible_duplicates)

    GrievanceNotification.send_all_notifications(GrievanceNotification.prepare_notification_for_ticket_creation(ticket))

    return ticket, ticket_details


def create_needs_adjudication_tickets(
    individuals_queryset: QuerySet[Individual],
    results_key: str,
    business_area: BusinessArea,
    registration_data_import: Optional[RegistrationDataImport] = None,
) -> Optional[List[TicketNeedsAdjudicationDetails]]:
    from hct_mis_api.apps.household.models import Individual

    if not individuals_queryset:
        return None

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
            registration_data_import=registration_data_import,
            possible_duplicates=possible_duplicates,
            is_multiple_duplicates_version=True,
        )

        if ticket and ticket_details:
            linked_tickets.append(ticket)
            ticket_details_to_create.append(ticket_details)

        for ticket in linked_tickets:
            ticket.linked_tickets.set([t for t in linked_tickets if t != ticket])

    return ticket_details_to_create


def mark_as_duplicate_individual_and_reassign_roles(
    ticket_details: TicketNeedsAdjudicationDetails,
    individual_to_remove: Individual,
    user: AbstractUser,
    unique_individual: Individual,
) -> None:
    if ticket_details.is_multiple_duplicates_version:
        household = reassign_roles_on_disable_individual_service(
            individual_to_remove,
            ticket_details.role_reassign_data,
            user,
            "new_individual",
        )
    else:
        household = reassign_roles_on_disable_individual_service(
            individual_to_remove, ticket_details.role_reassign_data, user
        )
    mark_as_duplicate_individual(individual_to_remove, unique_individual, household, user)


def mark_as_duplicate_individual(
    individual_to_remove: Individual, unique_individual: Individual, household: Household, user: AbstractUser
) -> None:
    old_individual = Individual.objects.get(id=individual_to_remove.id)

    individual_to_remove.mark_as_duplicate(unique_individual)

    log_create(Individual.ACTIVITY_LOG_MAPPING, "business_area", user, old_individual, individual_to_remove)
    household.refresh_from_db()
    if household.active_individuals.count() == 0:
        household.withdraw()
