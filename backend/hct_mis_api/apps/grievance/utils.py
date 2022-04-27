from django.shortcuts import get_object_or_404

from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.core.utils import decode_id_string


def get_individual(individual_id: str) -> Individual:
    decoded_selected_individual_id = decode_id_string(individual_id)
    individual = get_object_or_404(Individual, id=decoded_selected_individual_id)
    return individual


def select_individual(
        ticket_details: TicketNeedsAdjudicationDetails,
        selected_individual: list(Individual),
        ticket_duplicates: list(Individual),
        ticket_individuals: list(Individual)
):
    if selected_individual in ticket_duplicates and selected_individual not in ticket_individuals:
        ticket_details.selected_individuals.add(selected_individual)

        logger.info(
            "Individual with id: %s added to ticket %s", str(selected_individual.id), str(ticket.id)
        )


def unselect_individual(
        ticket_details: TicketNeedsAdjudicationDetails,
        selected_individuals: list(Individual),
        ticket_individuals: list(Individual)
):
    individuals_to_unselect = [
        individual for individual in ticket_individuals if individual not in selected_individuals
    ]

    if individuals_to_unselect:
        for individual in individuals_to_unselect:
            ticket_details.selected_individuals.remove(individual)

            logger.info(
                "Individual with id: %s removed from ticket %s", str(individual.id), str(ticket.id)
            )


def traverse_sibling_tickets(
        grievance_ticket: GrievanceTicket,
        selected_individual: list(Individual),
        selected_individuals: list(Individual)
):
    sibling_tickets = GrievanceTicket.objects.filter(
        registration_data_import_id=grievance_ticket.registration_data_import_id
    )

    for ticket in sibling_tickets:
        ticket_details = ticket.ticket_details
        ticket_duplicates = ticket_details.possible_duplicates.all()
        ticket_individuals = ticket_details.selected_individuals.all()

        select_individual(ticket_details, selected_individual, ticket_duplicates, ticket_individuals)
        unselect_individual(ticket_details, selected_individuals, ticket_individuals)
