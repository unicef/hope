import logging
import os
from typing import Dict, List, Union

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.grievance.models import (
    GrievanceDocument,
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.grievance.validators import validate_file
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


def create_grievance_documents(user: AbstractUser, grievance_ticket: GrievanceTicket, documents: List[Dict]) -> None:
    grievance_documents = []
    for document in documents:
        file = document["file"]
        validate_file(file)

        grievance_document = GrievanceDocument(
            name=document["name"],
            file=file,
            created_by=user,
            grievance_ticket=grievance_ticket,
            file_size=file.size,
            content_type=file.content_type,
        )
        grievance_documents.append(grievance_document)
    GrievanceDocument.objects.bulk_create(grievance_documents)


def update_grievance_documents(documents: List[Dict]) -> None:
    for document in documents:
        current_document = GrievanceDocument.objects.filter(id=decode_id_string(document["id"])).first()
        if current_document:
            os.remove(current_document.file.path)

            file = document.get("file")
            validate_file(file)

            current_document.name = document.get("name")
            current_document.file = file
            current_document.file_size = file.size
            current_document.content_type = file.content_type
            current_document.save()


def delete_grievance_documents(ticket_id: str, ids_to_delete: List[str]) -> None:
    documents_to_delete = GrievanceDocument.objects.filter(
        grievance_ticket_id=ticket_id, id__in=[decode_id_string(document_id) for document_id in ids_to_delete]
    )

    for document in documents_to_delete:
        os.remove(document.file.path)

    documents_to_delete.delete()
