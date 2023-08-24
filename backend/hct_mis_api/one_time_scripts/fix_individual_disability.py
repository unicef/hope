import logging

from django.db.models import Q, QuerySet

from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
)
from hct_mis_api.apps.household.models import DISABLED, NOT_DISABLED, Individual

logger = logging.getLogger(__name__)


def fix_individual_disability() -> None:
    # disability = "not disabled"
    tickets = (
        TicketAddIndividualDetails.objects.filter(
            individual_data__disability=True,
            individual_data__seeing_disability__isnull=True,
            individual_data__hearing_disability__isnull=True,
            individual_data__physical_disability__isnull=True,
            individual_data__memory_disability__isnull=True,
            individual_data__selfcare_disability__isnull=True,
            individual_data__comms_disability__isnull=True,
        )
        .filter(Q(individual_data__observed_disability__isnull=True) | Q(individual_data__observed_disability=[]))
        .select_related("ticket")
        .only("individual_data", "household_id", "ticket__status")
    )
    logger.info(f"Found {tickets.count()} tickets with disability = 'not disabled'")

    update_tickets_and_individuals(tickets, NOT_DISABLED)

    # disability = "disabled"
    tickets = (
        TicketAddIndividualDetails.objects.filter(individual_data__disability=True)
        .filter(
            Q(Q(individual_data__observed_disability__isnull=False) & ~Q(individual_data__observed_disability=[]))
            | Q(individual_data__seeing_disability__isnull=False)
            | Q(individual_data__hearing_disability__isnull=False)
            | Q(individual_data__physical_disability__isnull=False)
            | Q(individual_data__memory_disability__isnull=False)
            | Q(individual_data__selfcare_disability__isnull=False)
            | Q(individual_data__comms_disability__isnull=False)
        )
        .distinct()
        .select_related("ticket")
        .only("individual_data", "household_id", "ticket__status")
    )
    logger.info(f"Found {tickets.count()} tickets with disability = 'disabled'")

    update_tickets_and_individuals(tickets, DISABLED)
    logger.info("Tickets and individuals have been updated")


def update_tickets_and_individuals(tickets: QuerySet[TicketAddIndividualDetails], disability: str) -> None:
    tickets_to_update = []
    individuals_to_update = []

    for ticket in tickets:
        individual_data = ticket.individual_data
        individual_data["disability"] = disability
        tickets_to_update.append(TicketAddIndividualDetails(id=ticket.id, individual_data=individual_data))
        if ticket.ticket.status == GrievanceTicket.STATUS_CLOSED:
            individuals_to_update.append((ticket.household_id, individual_data["full_name"]))
    TicketAddIndividualDetails.objects.bulk_update(tickets_to_update, fields=("individual_data",))
    for household_id, full_name in individuals_to_update:
        Individual.objects.filter(household_id=household_id, full_name=full_name, disability=True).update(
            disability=disability
        )
