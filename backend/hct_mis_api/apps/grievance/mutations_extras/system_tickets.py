from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.grievance.mutations_extras.utils import (
    mark_as_duplicate_individual_and_reassign_roles,
    reassign_roles_on_disable_individual,
)
from hct_mis_api.apps.household.models import UNIQUE, UNIQUE_IN_BATCH, Individual
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask


def close_system_flagging_ticket(grievance_ticket, info, should_log=True):
    ticket_details = grievance_ticket.ticket_details

    if not ticket_details:
        return

    individual = ticket_details.golden_records_individual
    old_individual = copy_model_object(individual)

    if ticket_details.approve_status is False:
        individual.sanction_list_possible_match = False
        individual.save()
    else:
        individual.sanction_list_confirmed_match = True
        individual.save()
        reassign_roles_on_disable_individual(individual, ticket_details.role_reassign_data, info)

    if should_log:
        log_create(
            Individual.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_individual,
            individual,
        )


def _clear_deduplication_individuals_fields(individuals) -> None:
    for individual in individuals:
        individual.deduplication_golden_record_status = UNIQUE
        individual.deduplication_batch_status = UNIQUE_IN_BATCH
        individual.deduplication_golden_record_results = {}
        individual.deduplication_batch_results = {}
        DeduplicateTask.hard_deduplicate_documents(individual.documents.all())
    Individual.objects.bulk_update(
        individuals,
        [
            "deduplication_golden_record_status",
            "deduplication_batch_status",
            "deduplication_golden_record_results",
            "deduplication_batch_results",
        ],
    )


def close_needs_adjudication_old_ticket(ticket_details, info):
    both_individuals = (ticket_details.golden_records_individual, ticket_details.possible_duplicate)

    if ticket_details.selected_individual is None:
        _clear_deduplication_individuals_fields(both_individuals)
    else:
        individual_to_remove = ticket_details.selected_individual
        unique_individuals = [individual for individual in both_individuals if individual.id != individual_to_remove.id]
        mark_as_duplicate_individual_and_reassign_roles(
            ticket_details, individual_to_remove, info, unique_individuals[0]
        )
        _clear_deduplication_individuals_fields(unique_individuals)


def close_needs_adjudication_new_ticket(ticket_details, info):
    individuals = (ticket_details.golden_records_individual, *ticket_details.possible_duplicates.all())
    selected_individuals = ticket_details.selected_individuals.all()

    if not selected_individuals:
        _clear_deduplication_individuals_fields(individuals)
    else:
        unique_individuals = [individual for individual in individuals if individual not in selected_individuals]
        for individual_to_remove in selected_individuals:
            mark_as_duplicate_individual_and_reassign_roles(
                ticket_details, individual_to_remove, info, unique_individuals[0]
            )
        _clear_deduplication_individuals_fields(unique_individuals)


def close_needs_adjudication_ticket(grievance_ticket, info):
    ticket_details = grievance_ticket.ticket_details
    if not ticket_details:
        return

    if ticket_details.is_multiple_duplicates_version:
        close_needs_adjudication_new_ticket(ticket_details, info)
    else:
        close_needs_adjudication_old_ticket(ticket_details, info)
