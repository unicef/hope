from hct_mis_api.apps.grievance.models import GrievanceTicket


def select_individual(ticket, selected_individual, ticket_possible_duplicates, ticket_selected_individuals):
    if selected_individual in ticket_possible_duplicates and selected_individual not in ticket_selected_individuals:
        ticket.ticket_details.selected_individuals.add(selected_individual)

        logger.info(
            "Individual with id: %s added to ticket %s", str(selected_individual.id), str(ticket.id)
        )


def unselect_individual(ticket, selected_individuals, ticket_selected_individuals):
    individuals_to_unselect = [
        individual for individual in ticket_selected_individuals
        if individual not in selected_individuals
    ]

    if individuals_to_unselect:
        for individual in individuals_to_unselect:
            ticket.ticket_details.selected_individuals.remove(individual)

            logger.info(
                "Individual with id: %s removed from ticket %s", str(individual.id), str(ticket.id)
            )


def traverse_sibling_tickets(grievance_ticket, selected_individual, selected_individuals):
    sibling_tickets = GrievanceTicket.objects.filter(
        registration_data_import_id=grievance_ticket.registration_data_import_id
    )

    for ticket in sibling_tickets:
        ticket_possible_duplicates = ticket.ticket_details.possible_duplicates.all()
        ticket_selected_individuals = ticket.ticket_details.selected_individuals.all()

        select_individual(ticket, selected_individual, ticket_possible_duplicates, ticket_selected_individuals)
        unselect_individual(ticket, selected_individuals, ticket_selected_individuals)
