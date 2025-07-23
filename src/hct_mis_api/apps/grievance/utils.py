import logging
import os
from typing import Any, Callable

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.account.models import Partner, User
from hct_mis_api.apps.account.permissions import Permissions
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
    return get_object_or_404(Individual.objects.select_related("household"), id=decoded_selected_individual_id)


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

    selected_individuals_set = {str(i.id) for i in selected_individuals}
    for ticket_details in ticket_details_queryset:
        possible_duplicates_set = {str(i.id) for i in ticket_details.possible_duplicates.all()}.union(
            {str(ticket_details.golden_records_individual.id)}
        )
        intersection = selected_individuals_set.intersection(possible_duplicates_set)
        ticket_details.selected_individuals.add(*intersection)
        ticket_details.populate_cross_area_flag()


def clear_cache(
    ticket_details: TicketHouseholdDataUpdateDetails
    | TicketDeleteHouseholdDetails
    | TicketAddIndividualDetails
    | TicketIndividualDataUpdateDetails
    | TicketDeleteIndividualDetails,
    business_area_slug: str,
) -> None:
    if isinstance(ticket_details, TicketHouseholdDataUpdateDetails | TicketDeleteHouseholdDetails):
        cache.delete_pattern(f"count_{business_area_slug}_HouseholdNodeConnection_*")

    if isinstance(
        ticket_details,
        TicketAddIndividualDetails | TicketIndividualDataUpdateDetails | TicketDeleteIndividualDetails,
    ):
        cache.delete_pattern(f"count_{business_area_slug}_IndividualNodeConnection_*")


def create_grievance_documents(user: AbstractUser, grievance_ticket: GrievanceTicket, documents: list[dict]) -> None:
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


def update_grievance_documents(documents: list[dict]) -> None:
    for document in documents:
        current_document = GrievanceDocument.objects.filter(id=document["id"]).first()
        if current_document:
            os.remove(current_document.file.path)

            file = document.get("file")
            validate_file(file)

            current_document.name = document.get("name")
            current_document.file = file
            current_document.file_size = file.size
            current_document.content_type = file.content_type
            current_document.save()


def delete_grievance_documents(ticket_id: str, documents_to_delete: list[str]) -> None:
    documents_to_delete = GrievanceDocument.objects.filter(grievance_ticket_id=ticket_id, id__in=documents_to_delete)

    for document in documents_to_delete:
        os.remove(document.file.path)

    documents_to_delete.delete()


def filter_grievance_tickets_based_on_partner_areas_2(
    queryset: QuerySet["GrievanceTicket"],
    user: User,
    business_area_id: str,
    program_id: str | None,
    permissions: list[Permissions],
) -> QuerySet["GrievanceTicket"]:
    return filter_based_on_partner_areas_2(
        queryset=queryset,
        user=user,
        business_area_id=business_area_id,
        program_id=program_id,
        lookup_id="programs__id__in",
        id_container=lambda program_id: [program_id],
        permissions=permissions,
    )


def filter_feedback_based_on_partner_areas_2(
    queryset: QuerySet["Feedback"],
    user: User,
    business_area_id: str,
    program_id: str | None,
    permissions: list[Permissions],
) -> QuerySet["Feedback"]:
    return filter_based_on_partner_areas_2(
        queryset=queryset,
        user=user,
        business_area_id=business_area_id,
        program_id=program_id,
        lookup_id="program__id__in",
        id_container=lambda program_id: [program_id],
        permissions=permissions,
    )


def filter_based_on_partner_areas_2(
    queryset: QuerySet["GrievanceTicket", "Feedback"],
    user: User,
    business_area_id: str,
    program_id: str | None,
    lookup_id: str,
    id_container: Callable[[Any], list[Any]],
    permissions: list[Permissions],
) -> QuerySet["GrievanceTicket", "Feedback"]:
    try:
        programs_for_business_area = []
        filter_q = Q()
        if program_id:  # and user.has_program_access(program_id):
            programs_for_business_area = [program_id]
        else:
            programs_for_business_area = user.get_program_ids_for_permissions_in_business_area(
                business_area_id=business_area_id, permissions=permissions
            )
        # if user does not have access to any program/selected program -> return empty queryset for program-related obj
        if not programs_for_business_area:
            return queryset.model.objects.none()

        for program_id in programs_for_business_area:
            program_q = Q(**{lookup_id: id_container(program_id)})
            areas_null_and_program_q = program_q & Q(admin2__isnull=True)
            # apply admin area limits if partner has restrictions
            area_limits = user.partner.get_area_limits_for_program(program_id)
            areas_query = Q(admin2__in=area_limits) if area_limits.exists() else Q()

            filter_q |= Q(areas_null_and_program_q | Q(program_q & areas_query))

        # add Feedbacks without program for "All Programmes" query
        if queryset.model is Feedback and not program_id:
            filter_q |= Q(program__isnull=True)

        return queryset.filter(filter_q)
    except (Partner.DoesNotExist, AssertionError):
        return queryset.model.objects.none()


def validate_individual_for_need_adjudication(
    partner: Partner, individual: Individual, ticket_details: TicketNeedsAdjudicationDetails
) -> None:
    # Validate partner's permission
    if individual.household.admin2 and not partner.has_area_access(
        area_id=individual.household.admin2.id, program_id=individual.program.id
    ):
        raise PermissionDenied("Permission Denied: User does not have access to select individual")

    # validate Individual
    if individual not in list(ticket_details.possible_duplicates.all()) + [ticket_details.golden_records_individual] + [
        ticket_details.possible_duplicate
    ]:
        raise ValidationError(
            f"The selected individual {individual.unicef_id} is not valid, must be one of those attached to the ticket"
        )

    # validation for withdrawn Individual
    if individual.withdrawn:
        raise ValidationError(f"The selected individual {individual.unicef_id} is not valid, must be not withdrawn")


def validate_all_individuals_before_close_needs_adjudication(ticket_details: TicketNeedsAdjudicationDetails) -> None:
    duplicates_qs = ticket_details.selected_individuals.filter(withdrawn=False)
    distinct_qs = ticket_details.selected_distinct.filter(withdrawn=False)
    all_possible_duplicates = list(ticket_details.possible_duplicates.all()) + [
        ticket_details.golden_records_individual
    ]
    withdrawn_in_all_possible_duplicates = [i for i in all_possible_duplicates if i.withdrawn]

    # A user can flag all active individuals as duplicates but won’t be able to close the ticket
    if not distinct_qs and duplicates_qs.count() == (
        len(all_possible_duplicates) - len(withdrawn_in_all_possible_duplicates)
    ):
        raise ValidationError("Close ticket is not possible when all Individuals are flagged as duplicates")

    if not distinct_qs and (not withdrawn_in_all_possible_duplicates or not duplicates_qs):
        raise ValidationError(
            "Close ticket is possible when at least one individual is flagged as distinct or one of the individuals is withdrawn or duplicate"
        )

    for individual in all_possible_duplicates:
        if not individual.withdrawn and individual not in duplicates_qs and individual not in distinct_qs:
            raise ValidationError("Close ticket is possible when all active Individuals are flagged")
