import logging
from typing import List

from django.shortcuts import get_object_or_404

from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.models import Individual

logger = logging.getLogger(__name__)


def get_individual(individual_id: str) -> Individual:
    decoded_selected_individual_id = decode_id_string(individual_id)
    individual = get_object_or_404(Individual, id=decoded_selected_individual_id)
    return individual


def select_individual(
    ticket_details: TicketNeedsAdjudicationDetails,
    selected_individual: Individual,
    ticket_duplicates: List[Individual],
    ticket_individuals: List[Individual],
):
    if selected_individual in ticket_duplicates and selected_individual not in ticket_individuals:
        ticket_details.selected_individuals.add(selected_individual)

        logger.info("Individual with id: %s added to ticket %s", str(selected_individual.id), str(ticket_details.id))


def traverse_sibling_tickets(grievance_ticket: GrievanceTicket, selected_individual: Individual) -> None:
    sibling_tickets = GrievanceTicket.objects.filter(
        registration_data_import_id=grievance_ticket.registration_data_import.id
    )

    for ticket in sibling_tickets:
        ticket_details = ticket.ticket_details
        ticket_duplicates = ticket_details.possible_duplicates.all()
        ticket_individuals = ticket_details.selected_individuals.all()

        select_individual(ticket_details, selected_individual, ticket_duplicates, ticket_individuals)
