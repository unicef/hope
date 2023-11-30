import logging
import os
from typing import TYPE_CHECKING, Dict, List, Optional, Type, Union

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.geo.models import Area
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

if TYPE_CHECKING:
    from hct_mis_api.apps.accountability.models import Feedback

logger = logging.getLogger(__name__)


def get_individual(individual_id: str) -> Individual:
    decoded_selected_individual_id = decode_id_string(individual_id)
    individual = get_object_or_404(Individual.objects.select_related("household"), id=decoded_selected_individual_id)
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


def filter_tickets_based_on_partner_areas_2(
    queryset: QuerySet["GrievanceTicket", "Feedback"],
    user_partner: Partner,
    model: Type["GrievanceTicket", "Feedback"],
    business_area_id: str,
    program_id: Optional[str],
) -> QuerySet["GrievanceTicket", "Feedback"]:
    try:
        partner_permission = user_partner.get_permissions()

        if not program_id:
            # get all areas if no program_id, when info.context.headers.get("Program") == "all"
            program_area_ids = partner_permission.all_areas_for(str(business_area_id))
        else:
            program_area_ids = partner_permission.areas_for(str(business_area_id), str(program_id))
    except (Partner.DoesNotExist, AssertionError):
        return model.objects.none()

    if program_area_ids is None:  # If None, user's partner does not have permission
        return model.objects.none()
    elif not program_area_ids:  # If empty list, user's partner does have full permission
        pass
    else:  # Check to which areas user has access
        areas = Area.objects.filter(id__in=program_area_ids)
        areas_level_2 = areas.filter(level=1).values_list("id")

        queryset = queryset.filter(Q(admin2__in=areas_level_2) | Q(admin2__isnull=True))
    return queryset
