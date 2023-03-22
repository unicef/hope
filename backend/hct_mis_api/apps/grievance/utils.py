import logging
from typing import Union

from django.core.cache import cache
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.models import Individual

logger = logging.getLogger(__name__)


def get_individual(individual_id: str) -> Individual:
    decoded_selected_individual_id = decode_id_string(individual_id)
    individual = get_object_or_404(Individual, id=decoded_selected_individual_id)
    return individual


def traverse_sibling_tickets(grievance_ticket: GrievanceTicket, selected_individuals: QuerySet[Individual]) -> None:
    rdi = grievance_ticket.registration_data_import
    if not rdi:
        return

    ticket_details_queryset = (
        (
            TicketNeedsAdjudicationDetails.objects.filter(
                Q(possible_duplicates__in=selected_individuals) | Q(golden_records_individual__in=selected_individuals)
            ).exclude(Q(ticket__status=GrievanceTicket.STATUS_CLOSED) | Q(ticket__id=grievance_ticket.id))
        )
        .prefetch_related("possible_duplicates")
        .distinct()
    )

    selected_individuals_set = set([str(i.id) for i in selected_individuals])
    for ticket_details in ticket_details_queryset:
        possible_duplicates_set = set([str(i.id) for i in ticket_details.possible_duplicates.all()]).union(
            {str(ticket_details.golden_records_individual.id)}
        )
        intersection = selected_individuals_set.intersection(possible_duplicates_set)
        ticket_details.selected_individuals.add(*intersection)


def clear_cache(
    ticket_details: Union[
        TicketHouseholdDataUpdateDetails,
        TicketDeleteHouseholdDetails,
        TicketAddIndividualDetails,
        TicketIndividualDataUpdateDetails,
        TicketDeleteIndividualDetails,
    ],
    business_area_slug: str,
) -> None:
    if isinstance(ticket_details, (TicketHouseholdDataUpdateDetails, TicketDeleteHouseholdDetails)):
        cache.delete_pattern(f"count_{business_area_slug}_HouseholdNodeConnection_*")

    if isinstance(
        ticket_details,
        (TicketAddIndividualDetails, TicketIndividualDataUpdateDetails, TicketDeleteIndividualDetails),
    ):
        cache.delete_pattern(f"count_{business_area_slug}_IndividualNodeConnection_*")
