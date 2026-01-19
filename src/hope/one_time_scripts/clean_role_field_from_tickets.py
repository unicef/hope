"""
One-time script to clean the 'role' field from unclosed Add Individual and Individual Data Update tickets.

This script removes the deprecated 'role' field from the individual_data JSON field in tickets
that have not been closed yet. The role field was removed from the ticket processing logic
but some existing tickets still have it, causing errors when trying to close them.

Usage:
    from hope.one_time_scripts.clean_role_field_from_tickets import clean_role_field_from_tickets
    clean_role_field_from_tickets()
"""

from django.db import transaction

from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketIndividualDataUpdateDetails,
)

def clean_role_field_from_tickets() -> None:
    """
    Clean the deprecated 'role' field from unclosed Add Individual and Individual Data Update tickets.

    This script will:
    - Process tickets that are NOT closed (status != CLOSED)
    - Process tickets that HAVE a 'role' field in individual_data
    - Remove ONLY the 'role' field, preserving all other data
    """
    add_individual_count = 0
    individual_data_update_count = 0

    # Get unclosed tickets
    unclosed_tickets = GrievanceTicket.objects.exclude(status=GrievanceTicket.STATUS_CLOSED)

    # Find Add Individual tickets with 'role' field in individual_data
    add_individual_tickets = TicketAddIndividualDetails.objects.filter(
        ticket__in=unclosed_tickets,
        individual_data__has_key="role",
    )

    # Find Individual Data Update tickets with 'role' field in individual_data
    individual_data_update_tickets = TicketIndividualDataUpdateDetails.objects.filter(
        ticket__in=unclosed_tickets,
        individual_data__has_key="role",
    )

    print(
        f"Found {add_individual_tickets.count()} Add Individual tickets "
        f"and {individual_data_update_tickets.count()} Individual Data Update tickets with 'role' field"
    )

    # Process Add Individual tickets
    with transaction.atomic():
        for ticket_details in add_individual_tickets:
            if ticket_details.individual_data and "role" in ticket_details.individual_data:
                print(
                    f"Removing 'role' field from Add Individual ticket {ticket_details.ticket.unicef_id} "
                    f"(ID: {ticket_details.ticket.id})"
                )
                individual_data = ticket_details.individual_data.copy()
                individual_data.pop("role", None)
                ticket_details.individual_data = individual_data
                ticket_details.save(update_fields=["individual_data"])
                add_individual_count += 1

    # Process Individual Data Update tickets
    with transaction.atomic():
        for ticket_details in individual_data_update_tickets:
            if ticket_details.individual_data and "role" in ticket_details.individual_data:
                print(
                    f"Removing 'role' field from Individual Data Update ticket {ticket_details.ticket.unicef_id} "
                    f"(ID: {ticket_details.ticket.id})"
                )
                individual_data = ticket_details.individual_data.copy()
                individual_data.pop("role", None)
                ticket_details.individual_data = individual_data
                ticket_details.save(update_fields=["individual_data"])
                individual_data_update_count += 1

    print(
        f"Cleaned 'role' field from {add_individual_count} Add Individual tickets "
        f"and {individual_data_update_count} Individual Data Update tickets"
    )

