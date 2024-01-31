import logging
import os
from typing import Any, Callable, Dict, List, Optional, Union

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.accountability.models import Feedback
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
        ticket_details.populate_cross_area_flag()


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


def filter_grievance_tickets_based_on_partner_areas_2(
    queryset: QuerySet["GrievanceTicket"],
    user_partner: Partner,
    business_area_id: str,
    program_id: Optional[str],
) -> QuerySet["GrievanceTicket"]:
    return filter_based_on_partner_areas_2(
        queryset=queryset,
        user_partner=user_partner,
        business_area_id=business_area_id,
        program_id=program_id,
        lookup_id="programs__id__in",
        id_container=lambda program_id: [program_id],
    )


def filter_feedback_based_on_partner_areas_2(
    queryset: QuerySet["Feedback"],
    user_partner: Partner,
    business_area_id: str,
    program_id: Optional[str],
) -> QuerySet["Feedback"]:
    return filter_based_on_partner_areas_2(
        queryset=queryset,
        user_partner=user_partner,
        business_area_id=business_area_id,
        program_id=program_id,
        lookup_id="program__id__in",
        id_container=lambda program_id: [program_id],
    )


def filter_based_on_partner_areas_2(
    queryset: QuerySet["GrievanceTicket", "Feedback"],
    user_partner: Partner,
    business_area_id: str,
    program_id: Optional[str],
    lookup_id: str,
    id_container: Callable[[Any], List[Any]],
) -> QuerySet["GrievanceTicket", "Feedback"]:
    business_area_id_str = str(business_area_id)
    try:
        partner_permission = user_partner.get_permissions()
        filter_q = Q()
        if program_id:
            areas = partner_permission.areas_for(business_area_id_str, str(program_id))
            if areas is None:
                return queryset.model.objects.none()
            programs_permissions = {str(program_id): areas}.items()
        else:
            if business_area_permission := partner_permission.get_programs_for_business_area(business_area_id_str):
                programs_permissions = business_area_permission.programs.items()
                if (
                    not programs_permissions
                ):  # if user does not have permission to any program in this business area -> only non-program tickets
                    return queryset.model.objects.none()
            else:
                return queryset.model.objects.none()
        for perm_program_id, areas_ids in programs_permissions:
            program_q = Q(**{lookup_id: id_container(perm_program_id)})
            areas_null_and_program_q = program_q & Q(admin2__isnull=True)
            if areas_ids:
                filter_q |= Q(areas_null_and_program_q | Q(program_q & Q(admin2__in=areas_ids)))
            else:
                filter_q |= program_q  # empty areas -> full area access

        # add Feedbacks without program for "All Programmes" query
        if queryset.model is Feedback and not program_id:
            filter_q |= Q(program__isnull=True)

        queryset = queryset.filter(filter_q)
        return queryset
    except (Partner.DoesNotExist, AssertionError):
        return queryset.model.objects.none()
