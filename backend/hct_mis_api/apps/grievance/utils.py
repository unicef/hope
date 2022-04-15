import logging

from .models import GrievanceTicket


logger = logging.getLogger(__name__)


def remove_individual_from_multiple_duplicated_ticket(selected_individual, registration_data_import_id):
    siblings_tickets = GrievanceTicket.objects.filter(
        registration_data_import_id=registration_data_import_id
    )

    for ticket in siblings_tickets:
        possible_duplicates = ticket.ticket_details.possible_duplicates.all()
        if selected_individual in possible_duplicates:
            ticket.ticket_details.possible_duplicates.remove(selected_individual)
            logger.info("Individual %s was removed", selected_individual.id)
