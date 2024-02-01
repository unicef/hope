import copy
import logging
from typing import Any

from django.db.models import Q, QuerySet

from hct_mis_api.apps.grievance.models import (
    GrievanceDocument,
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails,
    TicketNote,
    TicketPaymentVerificationDetails,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.one_time_scripts.migrate_data_for_sync import (
    get_household_representation_per_program_by_old_household_id,
    get_individual_representation_per_program_by_old_individual_id,
)
from hct_mis_api.one_time_scripts.migrate_grievance_for_sync import (
    copy_grievance_ticket,
    copy_ticket_with_household,
    copy_ticket_with_individual,
    handle_bulk_create_paginated_data,
    handle_bulk_update_representations_household_unicef_id,
    handle_extra_data,
    handle_role_reassign_data,
)

rdi_list_dict = [
    {
        "rdi_id": "dd4edad1-bc79-4b29-ad0b-64b5f9880730",
        "wrong_program_id": "d3453d26-4dfd-4754-9509-199409d664e0",
        "good_program_id": "1b9ae544-ad2f-492a-87ed-b0d2ea69d62e",
    },
    {
        "rdi_id": "e53e277b-2abb-46a0-9dd5-f84622f500a1",
        "wrong_program_id": "c5f1caa6-68b6-4c68-8ae5-d6a180d68666",
        "good_program_id": "5d9d2eec-a51f-4613-8494-ee96b4bb3f2b",
    },
    {
        "rdi_id": "294082c6-2911-489e-8cbe-39701be3a9fc",
        "wrong_program_id": "a16e88a9-a2ed-44b8-828d-13ee7cf8d92f",
        "good_program_id": "60018500-f548-4334-80b6-4e33d53746be",
    },
    {
        "rdi_id": "99037d0b-0a6c-4b92-969e-ecac793498f5",
        "wrong_program_id": "a16e88a9-a2ed-44b8-828d-13ee7cf8d92f",
        "good_program_id": "60018500-f548-4334-80b6-4e33d53746be",
    },
    {
        "rdi_id": "cb02f7a2-1de3-4a62-becb-969d5793f5ca",
        "wrong_program_id": "c6203ef4-f793-45fd-a322-c02480ff7c2e",
        "good_program_id": "c6203ef4-f793-45fd-a322-c02480ff7c2e",
    },
    {
        "rdi_id": "cc96e2d0-7ed1-44fc-90d2-c4c430e1e92b",
        "wrong_program_id": "373a51cf-f4e3-405a-ba5a-14db65244496",
        "good_program_id": "d2090028-c216-4ec0-8734-7500a0386669",
    },
    {
        "rdi_id": "6b4a5350-1112-4e03-9f95-487e2c0464f3",
        "wrong_program_id": "d25d9093-2308-4b7f-ab0a-2fabf8809b66",
        "good_program_id": "d25d9093-2308-4b7f-ab0a-2fabf8809b66",
    },
    {
        "rdi_id": "0b3b9909-f214-4195-a093-ec5e661ed333",
        "wrong_program_id": "d3453d26-4dfd-4754-9509-199409d664e0",
        "good_program_id": "1b9ae544-ad2f-492a-87ed-b0d2ea69d62e",
    },
    {
        "rdi_id": "a09c1115-661c-409d-af56-460d913c157a",
        "wrong_program_id": "a16e88a9-a2ed-44b8-828d-13ee7cf8d92f",
        "good_program_id": "60018500-f548-4334-80b6-4e33d53746be",
    },
    {
        "rdi_id": "ca905acc-a67e-4e19-bf6a-503d613dfea9",
        "wrong_program_id": "edeefab7-08d0-4f91-a805-6e3afabdbfbb",
        "good_program_id": "edeefab7-08d0-4f91-a805-6e3afabdbfbb",
    },
    {
        "rdi_id": "cf4b391c-7106-4540-8655-2b1d11510ccf",
        "wrong_program_id": "96a3d4df-c6ac-4664-b631-9f284b85bad0",
        "good_program_id": "263b9684-0cda-4b8c-947a-a128912f301d",
    },
]
rdis = RegistrationDataImport.objects.filter(id__in=[rdi["rdi_id"] for rdi in rdi_list_dict])

logger = logging.getLogger(__name__)

BATCH_SIZE = 100


def create_tickets_for_missing_rdis(rdis: QuerySet) -> None:
    model_list = [
        TicketComplaintDetails,
        TicketSensitiveDetails,
        TicketPaymentVerificationDetails,
        TicketIndividualDataUpdateDetails,
        TicketHouseholdDataUpdateDetails,
        TicketAddIndividualDetails,
        TicketDeleteIndividualDetails,
        TicketDeleteHouseholdDetails,
        TicketSystemFlaggingDetails,
        TicketPositiveFeedbackDetails,
        TicketNegativeFeedbackDetails,
        TicketReferralDetails,
        TicketNeedsAdjudicationDetails,
        GrievanceTicket,
        TicketNote,
        GrievanceDocument,
    ]
    for model in model_list:
        model._meta.get_field("created_at").auto_now_add = False
    try:
        for rdi in rdis:
            logger.info(f"Creating tickets for {rdi}")
            program = rdi.program
            households_ids = list(
                Household.original_and_repr_objects.filter(registration_data_import=rdi, is_original=True).values_list(
                    "id", flat=True
                )
            )
            individuals_ids = list(
                Individual.original_and_repr_objects.filter(
                    Q(is_original=True)
                    & (Q(household__id__in=households_ids) | Q(represented_households__id__in=households_ids))
                ).values_list("id", flat=True)
            )
            handle_add_individual_details_for_fix(households_ids, program)
            handle_delete_household_details_for_fix(households_ids, program)
            handle_individual_data_update_details_for_fix(individuals_ids, program)
            handle_system_flagging_details_for_fix(individuals_ids, program)
            handle_needs_adjudication_details_for_fix(individuals_ids, program)
    finally:
        for model in model_list:
            model._meta.get_field("created_at").auto_now_add = True


def handle_add_individual_details_for_fix(households_ids: list, program: Program) -> None:
    logger.info("Handling TicketAddIndividualDetails")
    handle_tickets_with_household_for_fix(TicketAddIndividualDetails, households_ids, program)


def handle_delete_household_details_for_fix(households_ids: list, program: Program) -> None:
    logger.info("Handling TicketDeleteHouseholdDetails")
    handle_tickets_with_household_for_fix(TicketDeleteHouseholdDetails, households_ids, program)


def handle_individual_data_update_details_for_fix(individuals_ids: list, program: Program) -> None:
    logger.info("Handling TicketIndividualDataUpdateDetails")
    handle_tickets_with_individual_for_fix(TicketIndividualDataUpdateDetails, individuals_ids, program)


def handle_system_flagging_details_for_fix(individuals_ids: list, program: Program) -> None:
    logger.info("Handling TicketSystemFlaggingDetails")
    handle_tickets_with_individual_for_fix(
        TicketSystemFlaggingDetails, individuals_ids, program, individual_field_name="golden_records_individual"
    )


def handle_needs_adjudication_details_for_fix(individuals_ids: list, program: Program) -> None:
    logger.info("Handling TicketNeedsAdjudicationDetails")
    tickets = (
        TicketNeedsAdjudicationDetails.objects.select_related(
            "ticket",
            "golden_records_individual",
        )
        .filter(
            Q(ticket__is_original=True)
            & (Q(golden_records_individual__id__in=individuals_ids) | Q(possible_duplicates__id__in=individuals_ids))
        )
        .order_by("pk")
    )
    logger.info(f"Updating TicketNeedsAdjudicationDetails for program {program.name}")
    # adding individuals to existing copied tickets
    update_needs_adjudication_representations(tickets, program)

    # creating new tickets representations
    logger.info(f"Creating new TicketNeedsAdjudicationDetails for program {program.name}")
    create_new_needs_adjudication_representations(tickets, program)


def update_needs_adjudication_representations(tickets: QuerySet, program: Program) -> None:
    tickets_to_update = tickets.filter(ticket__copied_to__programs=program).order_by("pk")

    PossibleDuplicateThrough = TicketNeedsAdjudicationDetails.possible_duplicates.through
    SelectedIndividualThrough = TicketNeedsAdjudicationDetails.selected_individuals.through

    tickets_to_update_ids = list(tickets_to_update.values_list("id", flat=True))
    tickets_to_update_count = len(tickets_to_update_ids)
    logger.info(f"Tickets to handle: {tickets_to_update_count}")
    for batch_start in range(0, tickets_to_update_count, BATCH_SIZE):
        logger.info(f"Handling needs adjudication tickets: {batch_start} of {tickets_to_update_count}")
        batched_tickets_to_update_ids = tickets_to_update_ids[batch_start : batch_start + BATCH_SIZE]
        batched_tickets_to_update = TicketNeedsAdjudicationDetails.objects.filter(
            id__in=batched_tickets_to_update_ids
        ).select_related(
            "ticket",
            "golden_records_individual",
        )
        possible_duplicates_through_to_create = []
        select_through_to_create = []
        for original_needs_adjudication_ticket in batched_tickets_to_update:
            needs_adjudication_ticket_repr = (
                original_needs_adjudication_ticket.ticket.copied_to.filter(programs=program)
                .first()
                .needs_adjudication_ticket_details
            )
            individual_representations_from_original = [
                original_needs_adjudication_ticket.golden_records_individual.copied_to.filter(program=program).first(),
                *[
                    get_individual_representation_per_program_by_old_individual_id(
                        program=program,
                        old_individual_id=ind.id,
                    )
                    for ind in original_needs_adjudication_ticket.possible_duplicates(
                        manager="original_and_repr_objects"
                    ).only("id")
                ],
            ]
            # Delete None values
            individual_representations_from_original = [ind for ind in individual_representations_from_original if ind]
            individual_representations_from_copy = [
                needs_adjudication_ticket_repr.golden_records_individual,
                *needs_adjudication_ticket_repr.possible_duplicates.all(),
            ]
            for ind in individual_representations_from_original:
                if ind not in individual_representations_from_copy:
                    possible_duplicates_through_to_create.append(
                        PossibleDuplicateThrough(
                            ticketneedsadjudicationdetails=needs_adjudication_ticket_repr,
                            individual=ind,
                        )
                    )

            selected_individual_representations_from_original = [
                get_individual_representation_per_program_by_old_individual_id(
                    program=program,
                    old_individual_id=ind.id,
                )
                for ind in original_needs_adjudication_ticket.selected_individuals(
                    manager="original_and_repr_objects"
                ).only("id")
            ]
            # Delete None values
            selected_individual_representations_from_original = [
                ind for ind in selected_individual_representations_from_original if ind
            ]
            for ind in selected_individual_representations_from_original:
                select_through_to_create.append(
                    SelectedIndividualThrough(
                        ticketneedsadjudicationdetails=needs_adjudication_ticket_repr,
                        individual=ind,
                    )
                )
        PossibleDuplicateThrough.objects.bulk_create(possible_duplicates_through_to_create, ignore_conflicts=True)
        SelectedIndividualThrough.objects.bulk_create(select_through_to_create, ignore_conflicts=True)


def create_new_needs_adjudication_representations(tickets: QuerySet, program: Program) -> None:
    needs_adjudication_tickets = tickets.exclude(ticket__copied_to__programs=program).order_by("pk")

    PossibleDuplicateThrough = TicketNeedsAdjudicationDetails.possible_duplicates.through
    SelectedIndividualThrough = TicketNeedsAdjudicationDetails.selected_individuals.through
    needs_adjudication_tickets_ids = list(needs_adjudication_tickets.values_list("pk", flat=True))
    tickets_count = len(needs_adjudication_tickets_ids)
    logger.info(f"Tickets to handle: {tickets_count}")
    for batch_start in range(0, tickets_count, BATCH_SIZE):
        batched_ids = needs_adjudication_tickets_ids[batch_start : batch_start + BATCH_SIZE]
        needs_adjudication_tickets_batch = TicketNeedsAdjudicationDetails.objects.filter(
            id__in=batched_ids
        ).select_related(
            "ticket",
            "golden_records_individual",
        )
        logger.info(f"Handling needs adjudication tickets: {batch_start} of {tickets_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }

        new_possible_duplicates_to_create = []
        new_selected_individuals_to_create = []

        for needs_adjudication_ticket in needs_adjudication_tickets_batch:
            individuals = [
                needs_adjudication_ticket.golden_records_individual,
                *needs_adjudication_ticket.possible_duplicates(manager="original_and_repr_objects").all(),
            ]
            possible_duplicates_repr = [
                get_individual_representation_per_program_by_old_individual_id(
                    program=program,
                    old_individual_id=individual.id,
                )
                for individual in individuals
                if individual
            ]
            possible_duplicates_repr = [individual for individual in possible_duplicates_repr if individual]
            if len(possible_duplicates_repr) > 1:
                needs_adjudication_ticket_copy = copy.deepcopy(needs_adjudication_ticket)
                if hasattr(needs_adjudication_ticket_copy, "role_reassign_data"):
                    needs_adjudication_ticket_copy = handle_role_reassign_data(needs_adjudication_ticket_copy, program)
                if hasattr(needs_adjudication_ticket_copy, "extra_data"):
                    needs_adjudication_ticket_copy = handle_extra_data(needs_adjudication_ticket_copy, program)
                needs_adjudication_ticket_copy.pk = None
                # Copy Grievance Ticket
                grievance_ticket_data, notes_to_create, documents_to_create = copy_grievance_ticket(
                    needs_adjudication_ticket_copy,
                    program,
                    needs_adjudication_ticket,
                )
                objects_to_create_dict["notes"].extend(notes_to_create)
                objects_to_create_dict["documents"].extend(documents_to_create)
                objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                objects_to_create_dict["tickets"].append(needs_adjudication_ticket_copy)

                needs_adjudication_ticket_copy.golden_records_individual = possible_duplicates_repr.pop()

                # Handle selected_individuals
                old_selected_individuals = (
                    needs_adjudication_ticket.selected_individuals(manager="original_and_repr_objects")
                    .filter(is_original=True)
                    .all()
                )
                selected_individuals = [
                    get_individual_representation_per_program_by_old_individual_id(
                        program=program,
                        old_individual_id=individual,
                    )
                    for individual in old_selected_individuals
                ]
                selected_individuals = [individual for individual in selected_individuals if individual]

                new_possible_duplicates_to_create.extend(
                    [
                        PossibleDuplicateThrough(
                            ticketneedsadjudicationdetails=needs_adjudication_ticket_copy,
                            individual=individual,
                        )
                        for individual in possible_duplicates_repr
                    ]
                )
                new_selected_individuals_to_create.extend(
                    [
                        SelectedIndividualThrough(
                            ticketneedsadjudicationdetails=needs_adjudication_ticket_copy,
                            individual=individual,
                        )
                        for individual in selected_individuals
                    ]
                )

        handle_bulk_create_paginated_data([], objects_to_create_dict, TicketNeedsAdjudicationDetails)
        PossibleDuplicateThrough.objects.bulk_create(new_possible_duplicates_to_create)
        SelectedIndividualThrough.objects.bulk_create(new_selected_individuals_to_create)


def handle_tickets_with_household_for_fix(model: Any, households_ids: list, program: Program) -> None:
    tickets = (
        model.objects.select_related(
            "ticket",
            "household",
        )
        .filter(household__id__in=households_ids, ticket__is_original=True)
        .exclude(ticket__copied_to__programs=program)
    )
    tickets_to_handle = tickets.filter(
        (Q(ticket__status=GrievanceTicket.STATUS_CLOSED) & ~Q(ticket__copied_to__programs__is_visible=True))
        | ~Q(ticket__status=GrievanceTicket.STATUS_CLOSED)
    ).order_by("pk")
    tickets_to_handle_ids = list(tickets_to_handle.values_list("pk", flat=True))
    tickets_to_handle_count = len(tickets_to_handle_ids)
    logger.info(f"Found {tickets_to_handle_count} tickets to handle")
    for batch_start in range(0, tickets_to_handle_count, BATCH_SIZE):
        tickets_to_handle_batched_ids = tickets_to_handle_ids[batch_start : batch_start + BATCH_SIZE]
        tickets_to_handle_batch = model.objects.filter(id__in=tickets_to_handle_batched_ids).select_related(
            "ticket", "household"
        )
        logger.info(f"Handling tickets: {batch_start} of {tickets_to_handle_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        for ticket_to_handle in tickets_to_handle_batch:
            if household_representation := ticket_to_handle.household.copied_to.filter(program=program).first():
                ticket_copy, grievance_ticket_data, notes_to_create, documents_to_create = copy_ticket_with_household(
                    ticket_to_handle, program, household_representation=household_representation
                )
                if model == TicketDeleteHouseholdDetails:
                    ticket_copy.reason_household = get_household_representation_per_program_by_old_household_id(
                        program=program,
                        old_household_id=ticket_to_handle.reason_household,
                    )
                objects_to_create_dict["tickets"].append(ticket_copy)
                objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                objects_to_create_dict["documents"].extend(documents_to_create)
                objects_to_create_dict["notes"].extend(notes_to_create)
        handle_bulk_create_paginated_data([], objects_to_create_dict, model)

    tickets_with_hh_representation = model.objects.select_related(
        "ticket",
        "household",
    ).filter(
        household__isnull=False,
        ticket__is_original=False,
        ticket__copied_from__id__in=tickets_to_handle_ids,
        ticket__programs=program,
    )
    handle_bulk_update_representations_household_unicef_id(
        tickets_with_hh_representation,
        model,
    )


def handle_tickets_with_individual_for_fix(
    model: Any,
    individuals_ids: list,
    program: Program,
    individual_field_name: str = "individual",
) -> None:
    tickets = (
        model.objects.select_related(
            "ticket",
            individual_field_name,
        )
        .filter(**{f"{individual_field_name}__id__in": individuals_ids}, ticket__is_original=True)
        .exclude(ticket__copied_to__programs=program)
    )
    tickets_to_handle = tickets.filter(
        Q(Q(ticket__status=GrievanceTicket.STATUS_CLOSED) & ~Q(ticket__copied_to__programs__is_visible=True))
        | ~Q(ticket__status__in=[GrievanceTicket.STATUS_CLOSED])
    ).order_by("pk")
    tickets_to_handle_ids = list(tickets_to_handle.values_list("pk", flat=True))
    tickets_to_handle_count = len(tickets_to_handle_ids)
    logger.info(f"Found {tickets_to_handle_count} tickets to handle")
    for batch_start in range(0, tickets_to_handle_count, BATCH_SIZE):
        batched_ids = tickets_to_handle_ids[batch_start : batch_start + BATCH_SIZE]
        tickets_to_handle_batch = model.objects.select_related("ticket", individual_field_name).filter(
            id__in=batched_ids
        )
        logger.info(f"Handling tickets: {batch_start} of {tickets_to_handle_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        for ticket_to_handle in tickets_to_handle_batch:
            if individual_representation := (
                getattr(ticket_to_handle, individual_field_name).copied_to.filter(program=program).first()
            ):
                ticket_copy, grievance_ticket_data, notes_to_create, documents_to_create = copy_ticket_with_individual(
                    ticket_to_handle,
                    program,
                    individual_field_name=individual_field_name,
                    individual_representation=individual_representation,
                )
                objects_to_create_dict["tickets"].append(ticket_copy)
                objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                objects_to_create_dict["documents"].extend(documents_to_create)
                objects_to_create_dict["notes"].extend(notes_to_create)
        handle_bulk_create_paginated_data([], objects_to_create_dict, model)
