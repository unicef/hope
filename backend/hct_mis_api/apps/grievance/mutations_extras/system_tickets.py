from django.shortcuts import get_object_or_404

from core.utils import decode_id_string
from grievance.mutations_extras.utils import remove_individual_and_reassign_roles
from household.models import Individual, UNIQUE, UNIQUE_IN_BATCH


def close_system_flagging_ticket(grievance_ticket):
    ticket_details = grievance_ticket.ticket_details

    if not ticket_details:
        return

    individual = ticket_details.golden_records_individual

    if ticket_details.approve_status is False:
        individual.sanction_list_possible_match = False
        individual.save()
    else:
        remove_individual_and_reassign_roles(ticket_details, individual)


def _clear_deduplication_individuals_fields(individuals):
    for individual in individuals:
        individual.deduplication_golden_record_status = UNIQUE
        individual.deduplication_batch_status = UNIQUE_IN_BATCH
        individual.deduplication_golden_record_results = {}
        individual.deduplication_batch_results = {}
    Individual.objects.bulk_update(
        individuals,
        [
            "deduplication_golden_record_status",
            "deduplication_batch_status",
            "deduplication_golden_record_results",
            "deduplication_batch_results",
        ],
    )


def close_needs_adjudication_ticket(grievance_ticket):
    ticket_details = grievance_ticket.ticket_details
    individual_to_remove_id = decode_id_string(ticket_details.selected_individual)

    if not ticket_details:
        return

    both_individuals = (ticket_details.golden_records_individual, ticket_details.possible_duplicate)

    if ticket_details.selected_individual is None:
        _clear_deduplication_individuals_fields(both_individuals)
    else:
        individual_to_remove = get_object_or_404(Individual, id=individual_to_remove_id)
        unique_individuals = [
            individual for individual in both_individuals if str(individual.id) != individual_to_remove_id
        ]
        _clear_deduplication_individuals_fields(unique_individuals)
        remove_individual_and_reassign_roles(ticket_details, individual_to_remove)
