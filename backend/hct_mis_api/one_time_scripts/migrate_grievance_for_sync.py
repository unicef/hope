import copy
import logging
from itertools import chain
from typing import Any, Optional, Union

from django.db.models import Count, OuterRef, Q, QuerySet, Subquery
from django.utils import timezone

from hct_mis_api.apps.accountability.models import Feedback, FeedbackMessage, Message
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string, encode_id_base64
from hct_mis_api.apps.grievance.models import (
    GrievanceDocument,
    GrievanceTicket,
    GrievanceTicketThrough,
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
from hct_mis_api.apps.household.models import (
    BankAccountInfo,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import Payment, PaymentRecord
from hct_mis_api.apps.program.models import Program
from hct_mis_api.one_time_scripts.migrate_data_to_representations import (
    get_household_representation_per_program_by_old_household_id,
    get_individual_representation_per_program_by_old_individual_id,
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 100

ticket_grievance_ticket_field_name_mapping = {
    TicketComplaintDetails: "complaint_ticket_details",
    TicketSensitiveDetails: "sensitive_ticket_details",
    TicketPaymentVerificationDetails: "payment_verification_ticket_details",
    TicketIndividualDataUpdateDetails: "individual_data_update_ticket_details",
    TicketHouseholdDataUpdateDetails: "household_data_update_ticket_details",
    TicketAddIndividualDetails: "add_individual_ticket_details",
    TicketDeleteIndividualDetails: "delete_individual_ticket_details",
    TicketDeleteHouseholdDetails: "delete_household_ticket_details",
    TicketSystemFlaggingDetails: "system_flagging_ticket_details",
    TicketPositiveFeedbackDetails: "positive_feedback_ticket_details",
    TicketNegativeFeedbackDetails: "negative_feedback_ticket_details",
    TicketReferralDetails: "referral_ticket_details",
    TicketNeedsAdjudicationDetails: "needs_adjudication_ticket_details",
}


def migrate_grievance_to_representations() -> None:
    """
    Migrate grievance tickets and feedback into representations.
    """
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
        Message,
        Feedback,
        FeedbackMessage,
    ]
    for model in model_list:
        model._meta.get_field("created_at").auto_now_add = False
    try:
        migrate_grievance_tickets()
        migrate_messages()
        migrate_feedback()
        migrate_linked_tickets()
    finally:
        for model in model_list:
            model._meta.get_field("created_at").auto_now_add = True


def migrate_grievance_to_representations_per_business_area(business_area: Optional[BusinessArea] = None) -> None:
    """
    Migrate grievance tickets and feedback into representations per business area.
    """
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
        Message,
        Feedback,
        FeedbackMessage,
    ]
    for model in model_list:
        model._meta.get_field("created_at").auto_now_add = False
    try:
        migrate_grievance_tickets(business_area)
        migrate_messages(business_area)
        migrate_feedback(business_area)
        migrate_linked_tickets(business_area)
    finally:
        for model in model_list:
            model._meta.get_field("created_at").auto_now_add = True


def migrate_grievance_tickets(business_area: Optional[BusinessArea] = None) -> None:
    """
    Migrate grievance tickets into representations.
    """
    # print("Handle payment related tickets")
    # handle_payment_related_tickets()
    logger.info("Handle non payment related tickets")
    handle_non_payment_related_tickets(business_area)
    logger.info("Handle tickets not connected to any program")
    handle_non_program_tickets(business_area)


def handle_non_payment_related_tickets(business_area: Optional[BusinessArea] = None) -> None:
    """
    Copy grievance tickets to representations.
    Applied for tickets not connected to specific payment but connected to household or its individual.
    """
    logger.info("Handle TicketComplaintDetails without payment")
    handle_complaint_tickets_without_payments(business_area)
    logger.info("Handle TicketSensitiveDetails without payment")
    handle_sensitive_tickets_without_payments(business_area)
    logger.info("Handle TicketHouseholdDataUpdateDetails")
    handle_household_data_update_tickets(business_area)
    logger.info("Handle TicketIndividualDataUpdateDetails")
    handle_individual_data_update_tickets(business_area)
    logger.info("Handle TicketAddIndividualDetails")
    handle_add_individual_tickets(business_area)
    logger.info("Handle TicketDeleteIndividualDetails")
    handle_delete_individual_tickets(business_area)
    logger.info("Handle TicketDeleteHouseholdDetails")
    handle_delete_household_tickets(business_area)
    logger.info("Handle TicketSystemFlaggingDetails")
    handle_system_flagging_details_tickets(business_area)
    logger.info("Handle TicketPositiveFeedbackDetails")
    handle_positive_feedback_tickets(business_area)
    logger.info("Handle TicketNegativeFeedbackDetails")
    handle_negative_feedback_tickets(business_area)
    logger.info("Handle TicketReferralDetails")
    handle_referral_tickets(business_area)
    logger.info("Handle TicketNeedsAdjudicationDetails")
    handle_needs_adjudication_tickets(business_area)


def handle_complaint_tickets_without_payments(business_area: Optional[BusinessArea] = None) -> None:
    if business_area:
        filter_kwargs = {"ticket__business_area": business_area}
    else:
        filter_kwargs = {}
    complaint_tickets_without_payments = TicketComplaintDetails.objects.select_related(
        "ticket",
        "household",
        "individual",
    ).filter(
        payment_object_id__isnull=True, ticket__is_original=True, ticket__is_migration_handled=False, **filter_kwargs
    )
    handle_closed_tickets_with_household_and_individual(complaint_tickets_without_payments, TicketComplaintDetails)
    handle_active_tickets_with_household_and_individual(complaint_tickets_without_payments, TicketComplaintDetails)

    complaint_tickets_without_payments_representations = TicketComplaintDetails.objects.filter(
        payment_object_id__isnull=True, ticket__is_original=False, ticket__is_migration_handled=False, **filter_kwargs
    )
    handle_bulk_update_representations_household_unicef_id(
        complaint_tickets_without_payments_representations, TicketComplaintDetails
    )


def handle_sensitive_tickets_without_payments(business_area: Optional[BusinessArea] = None) -> None:
    if business_area:
        filter_kwargs = {"ticket__business_area": business_area}
    else:
        filter_kwargs = {}
    sensitive_tickets_without_payments = TicketSensitiveDetails.objects.select_related(
        "ticket",
        "household",
        "individual",
    ).filter(
        payment_object_id__isnull=True, ticket__is_original=True, ticket__is_migration_handled=False, **filter_kwargs
    )
    handle_closed_tickets_with_household_and_individual(sensitive_tickets_without_payments, TicketSensitiveDetails)
    handle_active_tickets_with_household_and_individual(sensitive_tickets_without_payments, TicketSensitiveDetails)

    sensitive_tickets_without_payments_representations = TicketSensitiveDetails.objects.filter(
        payment_object_id__isnull=True, ticket__is_original=False, ticket__is_migration_handled=False, **filter_kwargs
    )
    handle_bulk_update_representations_household_unicef_id(
        sensitive_tickets_without_payments_representations, TicketSensitiveDetails
    )


def handle_closed_tickets_with_household_and_individual(tickets: QuerySet, ticket_class: Any) -> None:
    """
    In case of closed complaint ticket, we need to copy the ticket to random representation of assigned
    household/individual.
    """
    logger.info("Handle closed tickets with household and individual")
    closed_tickets = tickets.filter(ticket__status=GrievanceTicket.STATUS_CLOSED).order_by("pk")
    closed_tickets_ids = list(closed_tickets.values_list("pk", flat=True))
    closed_count = len(closed_tickets_ids)
    logger.info(f"Tickets to handle: {closed_count}")
    for batch_start in range(0, closed_count, BATCH_SIZE):
        batched_ids = closed_tickets_ids[batch_start : batch_start + BATCH_SIZE]
        closed_tickets_batch = ticket_class.objects.filter(id__in=batched_ids).select_related(
            "ticket", "household", "individual"
        )
        logger.info(f"Handling closed tickets with household and individuals: {batch_start} of {closed_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        old_grievance_tickets_to_update = []
        for closed_ticket in closed_tickets_batch:
            household_representation = None
            individual_representation = None
            if closed_ticket.household:
                if household_representation := closed_ticket.household.copied_to.first():
                    program = household_representation.program
                    if closed_ticket.individual:
                        individual_representation = get_individual_representation_per_program_by_old_individual_id(
                            program=program,
                            old_individual_id=closed_ticket.individual,
                        )
            elif closed_ticket.individual:
                if individual_representation := closed_ticket.individual.copied_to.first():
                    program = individual_representation.program
            else:
                program = None

            if program:
                (
                    ticket_copy,
                    grievance_ticket_data,
                    notes_to_create,
                    documents_to_create,
                ) = copy_closed_ticket_with_household_and_individual(
                    closed_ticket, program, household_representation, individual_representation
                )
                objects_to_create_dict["tickets"].append(ticket_copy)
                objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                objects_to_create_dict["documents"].extend(documents_to_create)
                objects_to_create_dict["notes"].extend(notes_to_create)
                grievance_ticket = closed_ticket.ticket
                grievance_ticket.is_migration_handled = True
                old_grievance_tickets_to_update.append(grievance_ticket)
        handle_bulk_create_paginated_data(old_grievance_tickets_to_update, objects_to_create_dict, ticket_class)


def copy_closed_ticket_with_household_and_individual(
    closed_ticket: Any,
    program: Program,
    household_representation: Optional[Household] = None,
    individual_representation: Optional[Individual] = None,
) -> tuple:
    ticket_copy = copy.deepcopy(closed_ticket)
    ticket_copy.pk = None
    ticket_copy.household = household_representation
    ticket_copy.individual = individual_representation

    grievance_ticket_data, notes_to_create, documents_to_create = copy_grievance_ticket(
        ticket_copy, program, closed_ticket
    )
    return ticket_copy, grievance_ticket_data, notes_to_create, documents_to_create


def handle_active_tickets_with_household_and_individual(tickets: QuerySet, ticket_class: Any) -> None:
    """
    For active complaint tickets, we need to copy tickets for every household/individual representation
    """
    logger.info("Handle active tickets with household and individual")
    active_tickets = tickets.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED).order_by("pk")
    active_tickets_ids = list(active_tickets.values_list("pk", flat=True))
    active_count = len(active_tickets_ids)
    logger.info(f"Tickets to handle: {active_count}")
    for batch_start in range(0, active_count, BATCH_SIZE):
        batched_ids = active_tickets_ids[batch_start : batch_start + BATCH_SIZE]
        active_tickets_batch = ticket_class.objects.filter(id__in=batched_ids).select_related(
            "ticket", "household", "individual"
        )
        logger.info(f"Handling closed tickets with household and individuals: {batch_start} of {active_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        old_grievance_tickets_to_update = []
        for active_ticket in active_tickets_batch:
            if active_ticket.individual:
                individual_representations = active_ticket.individual.copied_to.all()
            else:
                individual_representations = Individual.objects.none()
            if active_ticket.household:
                household_representations = active_ticket.household.copied_to.all()
            else:
                household_representations = Household.objects.none()

            if individual_representations or household_representations:
                individual_programs = individual_representations.values_list("program", flat=True).distinct()
                household_programs = household_representations.values_list("program", flat=True).distinct()

                all_programs = household_programs.union(individual_programs)

                for program in all_programs:
                    (
                        ticket_copy,
                        grievance_ticket_data,
                        notes_to_create,
                        documents_to_create,
                    ) = copy_active_ticket_with_household_and_individual(active_ticket, program)
                    objects_to_create_dict["tickets"].append(ticket_copy)
                    objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                    objects_to_create_dict["documents"].extend(documents_to_create)
                    objects_to_create_dict["notes"].extend(notes_to_create)

                grievance_ticket = active_ticket.ticket
                grievance_ticket.is_migration_handled = True
                old_grievance_tickets_to_update.append(grievance_ticket)

        handle_bulk_create_paginated_data(old_grievance_tickets_to_update, objects_to_create_dict, ticket_class)


def copy_active_ticket_with_household_and_individual(active_ticket: Any, program: Program) -> tuple:
    ticket_copy = copy.deepcopy(active_ticket)
    ticket_copy.pk = None
    if ticket_copy.household:
        household_representation = get_household_representation_per_program_by_old_household_id(
            program=program,
            old_household_id=ticket_copy.household,
        )
        ticket_copy.household = household_representation

    if ticket_copy.individual:
        individual_representation = get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=ticket_copy.individual,
        )
        ticket_copy.individual = individual_representation

    grievance_ticket_data, notes_to_create, documents_to_create = copy_grievance_ticket(
        ticket_copy, program, active_ticket
    )
    return ticket_copy, grievance_ticket_data, notes_to_create, documents_to_create


def handle_tickets_with_household(model: Any, business_area: Optional[BusinessArea] = None) -> None:
    if business_area:
        filter_kwargs = {"ticket__business_area": business_area}
    else:
        filter_kwargs = {}
    tickets_with_hh = model.objects.select_related(
        "ticket",
        "household",
    ).filter(household__isnull=False, ticket__is_original=True, ticket__is_migration_handled=False, **filter_kwargs)
    logger.info(f"Tickets to handle: {tickets_with_hh.count()}")

    # Handle closed tickets - copy only for 1 random representation
    closed_tickets = tickets_with_hh.filter(ticket__status=GrievanceTicket.STATUS_CLOSED).order_by("pk")
    closed_tickets_ids = list(closed_tickets.values_list("pk", flat=True))
    closed_count = len(closed_tickets_ids)
    logger.info(f"Tickets to handle: {closed_count}")
    for batch_start in range(0, closed_count, BATCH_SIZE):
        closed_batched_ids = closed_tickets_ids[batch_start : batch_start + BATCH_SIZE]
        closed_tickets_batch = model.objects.filter(id__in=closed_batched_ids).select_related("ticket", "household")
        logger.info(f"Handling closed tickets with household and individuals: {batch_start} of {closed_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        old_grievance_tickets_to_update = []
        for closed_ticket in closed_tickets_batch:
            if household_representation := closed_ticket.household.copied_to.first():
                program = household_representation.program
                ticket_copy, grievance_ticket_data, notes_to_create, documents_to_create = copy_ticket_with_household(
                    closed_ticket, program, household_representation=household_representation
                )
                objects_to_create_dict["tickets"].append(ticket_copy)
                objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                objects_to_create_dict["documents"].extend(documents_to_create)
                objects_to_create_dict["notes"].extend(notes_to_create)
                grievance_ticket = closed_ticket.ticket
                grievance_ticket.is_migration_handled = True
                old_grievance_tickets_to_update.append(grievance_ticket)

        handle_bulk_create_paginated_data(old_grievance_tickets_to_update, objects_to_create_dict, model)

    # Handle active tickets - copy for all representations
    active_tickets = tickets_with_hh.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED).order_by("pk")
    active_tickets_ids = list(active_tickets.values_list("pk", flat=True))
    active_count = len(active_tickets_ids)
    logger.info(f"Tickets to handle: {active_count}")
    for batch_start in range(0, active_count, BATCH_SIZE):
        active_batched_ids = active_tickets_ids[batch_start : batch_start + BATCH_SIZE]
        active_tickets_batch = model.objects.filter(id__in=active_batched_ids).select_related("ticket", "household")
        logger.info(f"Handling closed tickets with household and individuals: {batch_start} of {active_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        old_grievance_tickets_to_update = []
        for active_ticket in active_tickets_batch:
            household_representations = active_ticket.household.copied_to.all()
            household_programs = household_representations.values_list("program", flat=True).distinct()

            for program in household_programs.iterator():
                ticket_copy, grievance_ticket_data, notes_to_create, documents_to_create = copy_ticket_with_household(
                    active_ticket, program
                )
                objects_to_create_dict["tickets"].append(ticket_copy)
                objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                objects_to_create_dict["documents"].extend(documents_to_create)
                objects_to_create_dict["notes"].extend(notes_to_create)

            grievance_ticket = active_ticket.ticket
            grievance_ticket.is_migration_handled = True
            old_grievance_tickets_to_update.append(grievance_ticket)

        handle_bulk_create_paginated_data(old_grievance_tickets_to_update, objects_to_create_dict, model)

    tickets_with_hh_representation = model.objects.select_related(
        "ticket",
        "household",
    ).filter(household__isnull=False, ticket__is_original=False, ticket__is_migration_handled=False, **filter_kwargs)
    handle_bulk_update_representations_household_unicef_id(
        tickets_with_hh_representation,
        model,
    )


def handle_tickets_delete_household_details(business_area: Optional[BusinessArea] = None) -> None:
    if business_area:
        filter_kwargs = {"ticket__business_area": business_area}
    else:
        filter_kwargs = {}
    tickets_with_hh = TicketDeleteHouseholdDetails.objects.select_related(
        "ticket",
        "household",
    ).filter(household__isnull=False, ticket__is_original=True, ticket__is_migration_handled=False, **filter_kwargs)
    logger.info(f"Tickets to handle: {tickets_with_hh.count()}")

    # Handle closed tickets - copy only for 1 random representation
    closed_tickets = tickets_with_hh.filter(ticket__status=GrievanceTicket.STATUS_CLOSED).order_by("pk")
    closed_tickets_ids = list(closed_tickets.values_list("pk", flat=True))
    closed_count = len(closed_tickets_ids)
    logger.info(f"Tickets to handle: {closed_count}")
    for batch_start in range(0, closed_count, BATCH_SIZE):
        closed_batched_ids = closed_tickets_ids[batch_start : batch_start + BATCH_SIZE]
        closed_tickets_batch = TicketDeleteHouseholdDetails.objects.filter(id__in=closed_batched_ids).select_related(
            "ticket", "household", "reason_household"
        )
        logger.info(f"Handling closed tickets with household and individuals: {batch_start} of {closed_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        old_grievance_tickets_to_update = []
        for closed_ticket in closed_tickets_batch:
            if household_representation := closed_ticket.household.copied_to.first():
                program = household_representation.program
                ticket_copy, grievance_ticket_data, notes_to_create, documents_to_create = copy_ticket_with_household(
                    closed_ticket, program, household_representation=household_representation
                )
                ticket_copy.reason_household = get_household_representation_per_program_by_old_household_id(
                    program=program,
                    old_household_id=closed_ticket.reason_household,
                )
                objects_to_create_dict["tickets"].append(ticket_copy)
                objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                objects_to_create_dict["documents"].extend(documents_to_create)
                objects_to_create_dict["notes"].extend(notes_to_create)
                grievance_ticket = closed_ticket.ticket
                grievance_ticket.is_migration_handled = True
                old_grievance_tickets_to_update.append(grievance_ticket)

        handle_bulk_create_paginated_data(
            old_grievance_tickets_to_update, objects_to_create_dict, TicketDeleteHouseholdDetails
        )

    # Handle active tickets - copy for all representations
    active_tickets = tickets_with_hh.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED).order_by("pk")
    active_tickets_ids = list(active_tickets.values_list("pk", flat=True))
    active_count = len(active_tickets_ids)
    logger.info(f"Tickets to handle: {active_count}")
    for batch_start in range(0, active_count, BATCH_SIZE):
        active_batched_ids = active_tickets_ids[batch_start : batch_start + BATCH_SIZE]
        active_tickets_batch = TicketDeleteHouseholdDetails.objects.filter(id__in=active_batched_ids).select_related(
            "ticket", "household", "reason_household"
        )
        logger.info(f"Handling closed tickets with household and individuals: {batch_start} of {active_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        old_grievance_tickets_to_update = []
        for active_ticket in active_tickets_batch:
            household_representations = active_ticket.household.copied_to.all()
            household_programs = household_representations.values_list("program", flat=True).distinct()

            for program in household_programs.iterator():
                ticket_copy, grievance_ticket_data, notes_to_create, documents_to_create = copy_ticket_with_household(
                    active_ticket, program
                )
                ticket_copy.reason_household = get_household_representation_per_program_by_old_household_id(
                    program=program,
                    old_household_id=active_ticket.reason_household,
                )
                objects_to_create_dict["tickets"].append(ticket_copy)
                objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                objects_to_create_dict["documents"].extend(documents_to_create)
                objects_to_create_dict["notes"].extend(notes_to_create)

            grievance_ticket = active_ticket.ticket
            grievance_ticket.is_migration_handled = True
            old_grievance_tickets_to_update.append(grievance_ticket)

        handle_bulk_create_paginated_data(
            old_grievance_tickets_to_update, objects_to_create_dict, TicketDeleteHouseholdDetails
        )

    tickets_with_hh_representation = TicketDeleteHouseholdDetails.objects.select_related(
        "ticket",
        "household",
    ).filter(household__isnull=False, ticket__is_original=False, ticket__is_migration_handled=False, **filter_kwargs)
    handle_bulk_update_representations_household_unicef_id(
        tickets_with_hh_representation,
        TicketDeleteHouseholdDetails,
    )


def copy_ticket_with_household(
    active_ticket: Any, program: Program, household_representation: Optional[Household] = None
) -> tuple:
    ticket = copy.deepcopy(active_ticket)
    if hasattr(ticket, "role_reassign_data"):
        ticket = handle_role_reassign_data(ticket, program)
    if not household_representation:
        household_representation = get_household_representation_per_program_by_old_household_id(
            program=program,
            old_household_id=ticket.household,
        )
    ticket.household = household_representation

    ticket.pk = None
    grievance_ticket_data, notes_to_create, documents_to_create = copy_grievance_ticket(ticket, program, active_ticket)
    return ticket, grievance_ticket_data, notes_to_create, documents_to_create


def handle_tickets_with_individual(
    model: Any, individual_field_name: str = "individual", business_area: Optional[BusinessArea] = None
) -> None:
    if business_area:
        filter_kwargs = {"ticket__business_area": business_area}
    else:
        filter_kwargs = {}
    tickets_with_ind = model.objects.select_related(
        "ticket",
        individual_field_name,
    ).filter(
        **{f"{individual_field_name}__isnull": False},
        ticket__is_original=True,
        ticket__is_migration_handled=False,
        **filter_kwargs,
    )
    logger.info(f"Tickets to handle: {tickets_with_ind.count()}")

    # Handle closed tickets
    closed_tickets = tickets_with_ind.filter(ticket__status=GrievanceTicket.STATUS_CLOSED).order_by("pk")
    closed_tickets_ids = list(closed_tickets.values_list("pk", flat=True))
    closed_count = len(closed_tickets_ids)
    for batch_start in range(0, len(closed_tickets_ids), BATCH_SIZE):
        batched_ids = closed_tickets_ids[batch_start : batch_start + BATCH_SIZE]
        closed_tickets_batch = model.objects.select_related("ticket", individual_field_name).filter(id__in=batched_ids)
        logger.info(f"Handling closed tickets with individual: {batch_start} of {closed_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        old_grievance_tickets_to_update = []
        for closed_ticket in closed_tickets_batch:
            if individual_representation := (getattr(closed_ticket, individual_field_name).copied_to.first()):
                program = individual_representation.program
                ticket_copy, grievance_ticket_data, notes_to_create, documents_to_create = copy_ticket_with_individual(
                    closed_ticket,
                    program,
                    individual_field_name=individual_field_name,
                    individual_representation=individual_representation,
                )
                objects_to_create_dict["tickets"].append(ticket_copy)
                objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                objects_to_create_dict["documents"].extend(documents_to_create)
                objects_to_create_dict["notes"].extend(notes_to_create)
                grievance_ticket = closed_ticket.ticket
                grievance_ticket.is_migration_handled = True
                old_grievance_tickets_to_update.append(grievance_ticket)

        handle_bulk_create_paginated_data(old_grievance_tickets_to_update, objects_to_create_dict, model)

    # Handle active tickets
    active_tickets = tickets_with_ind.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED).order_by("pk")
    active_tickets_ids = list(active_tickets.values_list("pk", flat=True))
    active_count = len(active_tickets_ids)
    logger.info(f"Tickets to handle: {active_count}")
    for batch_start in range(0, len(active_tickets_ids), BATCH_SIZE):
        batched_ids = active_tickets_ids[batch_start : batch_start + BATCH_SIZE]
        active_tickets_batch = model.objects.select_related("ticket", individual_field_name).filter(id__in=batched_ids)
        logger.info(f"Handling active tickets with individual: {batch_start} of {active_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        old_grievance_tickets_to_update = []
        for active_ticket in active_tickets_batch:
            individual_representations = getattr(active_ticket, individual_field_name).copied_to.all()
            individual_programs = individual_representations.values_list("program", flat=True).distinct()

            for program in individual_programs.iterator():
                ticket_copy, grievance_ticket_data, notes_to_create, documents_to_create = copy_ticket_with_individual(
                    active_ticket, program, individual_field_name=individual_field_name
                )
                objects_to_create_dict["tickets"].append(ticket_copy)
                objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                objects_to_create_dict["documents"].extend(documents_to_create)
                objects_to_create_dict["notes"].extend(notes_to_create)
            grievance_ticket = active_ticket.ticket
            grievance_ticket.is_migration_handled = True
            old_grievance_tickets_to_update.append(grievance_ticket)

        handle_bulk_create_paginated_data(old_grievance_tickets_to_update, objects_to_create_dict, model)


def copy_ticket_with_individual(
    active_ticket: Any,
    program: Program,
    individual_field_name: str,
    individual_representation: Optional[Individual] = None,
) -> tuple:
    ticket = copy.deepcopy(active_ticket)
    if hasattr(ticket, "role_reassign_data"):
        ticket = handle_role_reassign_data(ticket, program)
    if hasattr(active_ticket, "individual_data") and isinstance(active_ticket, TicketIndividualDataUpdateDetails):
        ticket = handle_individual_data(ticket, program)
    if not individual_representation:
        individual_representation = get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=getattr(ticket, individual_field_name),
        )
    setattr(ticket, individual_field_name, individual_representation)

    ticket.pk = None
    grievance_ticket_data, notes_to_create, documents_to_create = copy_grievance_ticket(ticket, program, active_ticket)
    return ticket, grievance_ticket_data, notes_to_create, documents_to_create


def handle_individual_data_update_tickets(business_area: Optional[BusinessArea] = None) -> None:
    handle_tickets_with_individual(TicketIndividualDataUpdateDetails, business_area=business_area)


def handle_household_data_update_tickets(business_area: Optional[BusinessArea] = None) -> None:
    handle_tickets_with_household(TicketHouseholdDataUpdateDetails, business_area=business_area)


def handle_add_individual_tickets(business_area: Optional[BusinessArea] = None) -> None:
    handle_tickets_with_household(TicketAddIndividualDetails, business_area=business_area)


def handle_delete_individual_tickets(business_area: Optional[BusinessArea] = None) -> None:
    handle_tickets_with_individual(TicketDeleteIndividualDetails, business_area=business_area)


def handle_delete_household_tickets(business_area: Optional[BusinessArea] = None) -> None:
    handle_tickets_delete_household_details(business_area=business_area)


def handle_system_flagging_details_tickets(business_area: Optional[BusinessArea] = None) -> None:
    handle_tickets_with_individual(
        TicketSystemFlaggingDetails, individual_field_name="golden_records_individual", business_area=business_area
    )


def handle_positive_feedback_tickets(business_area: Optional[BusinessArea] = None) -> None:
    if business_area:
        filter_kwargs = {"ticket__business_area": business_area}
    else:
        filter_kwargs = {}
    positive_feedback_tickets = TicketPositiveFeedbackDetails.objects.filter(
        ticket__is_original=True,
        ticket__is_migration_handled=False,
        **filter_kwargs,
    )
    handle_closed_tickets_with_household_and_individual(positive_feedback_tickets, TicketPositiveFeedbackDetails)
    handle_active_tickets_with_household_and_individual(positive_feedback_tickets, TicketPositiveFeedbackDetails)

    positive_feedback_tickets_representations = TicketPositiveFeedbackDetails.objects.filter(
        ticket__is_original=False,
        ticket__is_migration_handled=False,
        **filter_kwargs,
    )
    handle_bulk_update_representations_household_unicef_id(
        positive_feedback_tickets_representations,
        TicketPositiveFeedbackDetails,
    )


def handle_negative_feedback_tickets(business_area: Optional[BusinessArea] = None) -> None:
    if business_area:
        filter_kwargs = {"ticket__business_area": business_area}
    else:
        filter_kwargs = {}
    negative_feedback_tickets = TicketNegativeFeedbackDetails.objects.filter(
        ticket__is_original=True,
        ticket__is_migration_handled=False,
        **filter_kwargs,
    )
    handle_closed_tickets_with_household_and_individual(negative_feedback_tickets, TicketNegativeFeedbackDetails)
    handle_active_tickets_with_household_and_individual(negative_feedback_tickets, TicketNegativeFeedbackDetails)

    negative_feedback_tickets_representations = TicketNegativeFeedbackDetails.objects.filter(
        ticket__is_original=False,
        ticket__is_migration_handled=False,
        **filter_kwargs,
    )
    handle_bulk_update_representations_household_unicef_id(
        negative_feedback_tickets_representations,
        TicketNegativeFeedbackDetails,
    )


def handle_referral_tickets(business_area: Optional[BusinessArea] = None) -> None:
    if business_area:
        filter_kwargs = {"ticket__business_area": business_area}
    else:
        filter_kwargs = {}
    referral_tickets = TicketReferralDetails.objects.filter(
        ticket__is_original=True,
        ticket__is_migration_handled=False,
        **filter_kwargs,
    )
    handle_closed_tickets_with_household_and_individual(referral_tickets, TicketReferralDetails)
    handle_active_tickets_with_household_and_individual(referral_tickets, TicketReferralDetails)

    referral_tickets_representations = TicketReferralDetails.objects.filter(
        ticket__is_original=False,
        ticket__is_migration_handled=False,
        **filter_kwargs,
    )

    handle_bulk_update_representations_household_unicef_id(
        referral_tickets_representations,
        TicketReferralDetails,
    )


def handle_needs_adjudication_tickets(business_area: Optional[BusinessArea] = None) -> None:
    if business_area:
        filter_kwargs = {"ticket__business_area": business_area}
    else:
        filter_kwargs = {}
    needs_adjudication_tickets = (
        TicketNeedsAdjudicationDetails.objects.select_related(
            "ticket",
            "golden_records_individual",
        )
        .filter(ticket__is_original=True, ticket__is_migration_handled=False, **filter_kwargs)
        .order_by("pk")
    )

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
        old_grievance_tickets_to_update = []

        new_possible_duplicates_to_create = []
        new_selected_individuals_to_create = []

        for needs_adjudication_ticket in needs_adjudication_tickets_batch:
            individuals = [
                needs_adjudication_ticket.golden_records_individual,
                *needs_adjudication_ticket.possible_duplicates.all(),
            ]
            program_ids = (
                Individual.original_and_repr_objects.filter(id__in=[individual.id for individual in individuals])
                .values(
                    "copied_to__program",
                )
                .annotate(program_count=Count("id"))
                .filter(program_count__gt=1)
                .values_list("copied_to__program", flat=True)
            )
            programs = Program.objects.filter(id__in=program_ids)
            if not programs:
                grievance_ticket = needs_adjudication_ticket.ticket
                grievance_ticket.is_migration_handled = True
                old_grievance_tickets_to_update.append(grievance_ticket)
                continue

            for program in programs:
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

                possible_duplicates = [
                    get_individual_representation_per_program_by_old_individual_id(
                        program=program,
                        old_individual_id=individual,
                    )
                    for individual in individuals
                    if individual
                ]
                possible_duplicates = [individual for individual in possible_duplicates if individual]
                needs_adjudication_ticket_copy.golden_records_individual = possible_duplicates.pop()

                # Handle selected_individuals
                old_selected_individuals = needs_adjudication_ticket.selected_individuals.all()
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
                        for individual in possible_duplicates
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

            grievance_ticket = needs_adjudication_ticket.ticket
            grievance_ticket.is_migration_handled = True
            old_grievance_tickets_to_update.append(grievance_ticket)

        handle_bulk_create_paginated_data(
            old_grievance_tickets_to_update, objects_to_create_dict, TicketNeedsAdjudicationDetails
        )

        PossibleDuplicateThrough.objects.bulk_create(new_possible_duplicates_to_create)
        SelectedIndividualThrough.objects.bulk_create(new_selected_individuals_to_create)


def migrate_messages(business_area: Optional[BusinessArea] = None) -> None:
    logger.info("Handle Messages")
    if business_area:
        filter_kwargs = {"business_area": business_area}
    else:
        filter_kwargs = {}
    message_objects = (
        Message.original_and_repr_objects.select_related(
            "target_population",
            "target_population__program",
        )
        .filter(is_original=True, is_migration_handled=False, **filter_kwargs)
        .distinct()
    )

    message_objects_ids = list(message_objects.values_list("pk", flat=True))
    message_objects_count = len(message_objects_ids)
    logger.info(f"Messages to handle: {message_objects_count}")
    for batch_start in range(0, message_objects_count, BATCH_SIZE):
        message_objects_batched_ids = message_objects_ids[batch_start : batch_start + BATCH_SIZE]
        message_objects_batch = Message.original_and_repr_objects.filter(
            id__in=message_objects_batched_ids
        ).select_related(
            "target_population",
            "target_population__program",
        )
        logger.info(f"Handling  messages: {batch_start} of {message_objects_count}")
        new_messages_to_create = []
        message_household_to_create = []
        old_messages_to_update = []
        for message in message_objects_batch:
            if message.households(manager="original_and_repr_objects").exists():
                if message.target_population:
                    program = message.target_population.program
                    message_copy, message_household = copy_message(message, program)
                    new_messages_to_create.append(message_copy)
                    message_household_to_create.extend(message_household)

                    message.is_migration_handled = True
                    old_messages_to_update.append(message)
                else:
                    programs = list(
                        message.households(manager="original_and_repr_objects")
                        .values_list("copied_to__program", flat=True)
                        .distinct()
                    )
                    for program in programs:
                        message_copy, message_household = copy_message(message, program)
                        new_messages_to_create.append(message_copy)
                        message_household_to_create.extend(message_household)
                    message.is_migration_handled = True
                    old_messages_to_update.append(message)
        Message.objects.bulk_create(new_messages_to_create)
        MessageHouseholdRelation = Message.households.through
        MessageHouseholdRelation.objects.bulk_create(message_household_to_create)
        Message.objects.bulk_update(old_messages_to_update, ["is_migration_handled", "migrated_at"])
    logger.info("Handle Messages not connected to any program")
    handle_non_program_messages(business_area)


def copy_message(active_message: Message, program: Program) -> tuple:
    message = copy.deepcopy(active_message)
    message.pk = None
    message.is_original = False
    message.copied_from = active_message
    message.unicef_id = None
    if isinstance(program, Program):
        message.program = program
    else:
        message.program_id = program

    households_representations = [
        get_household_representation_per_program_by_old_household_id(
            program=program,
            old_household_id=household.id,
        )
        for household in active_message.households(manager="original_and_repr_objects").all().only("id")
    ]
    households_representations = [household for household in households_representations if household]
    MessageHouseholdRelation = Message.households.through
    message_household = [
        MessageHouseholdRelation(message=message, household_id=household.id) for household in households_representations
    ]
    return message, message_household


def migrate_feedback(business_area: Optional[BusinessArea] = None) -> None:
    logger.info("Handle Feedback objects")
    # Handle closed Feedback (Feedback related to a closed grievance ticket) OR Feedback with program
    copy_feedback_to_specific_program(business_area)
    # Handle active Feedback objects without program -
    # (Feedback with active tickets OR Feedback not related to any ticket) AND without defined program
    handle_active_feedback(business_area)
    logger.info("Handle Feedback not connected to any program")
    handle_non_program_feedback(business_area)


def copy_feedback_to_specific_program(business_area: Optional[BusinessArea] = None) -> None:
    if business_area:
        filter_kwargs = {"business_area": business_area}
    else:
        filter_kwargs = {}
    feedback_objects_for_specific_program = (
        Feedback.original_and_repr_objects.select_related(
            "program",
            "household_lookup",
            "individual_lookup",
            "linked_grievance",
            "household_lookup__program",
            "individual_lookup__program",
        )
        .filter(
            (Q(linked_grievance__status=GrievanceTicket.STATUS_CLOSED) | Q(program__isnull=False))
            & Q(is_original=True)
            & Q(is_migration_handled=False)
        )
        .filter(**filter_kwargs)
        .distinct()
    )
    logger.info("Handle Feedback objects with program or closed grievance ticket")

    feedback_objects_for_specific_program_ids = list(feedback_objects_for_specific_program.values_list("pk", flat=True))
    feedback_objects_for_specific_program_count = len(feedback_objects_for_specific_program_ids)
    logger.info(f"Feedback objects to handle: {feedback_objects_for_specific_program_count}")
    for batch_start in range(0, feedback_objects_for_specific_program_count, BATCH_SIZE):
        feedback_objects_for_specific_program_batched_ids = feedback_objects_for_specific_program_ids[
            batch_start : batch_start + BATCH_SIZE
        ]
        feedback_objects_for_specific_program_batch = Feedback.original_and_repr_objects.filter(
            id__in=feedback_objects_for_specific_program_batched_ids
        ).select_related(
            "program",
            "household_lookup",
            "individual_lookup",
            "linked_grievance",
            "household_lookup__program",
            "individual_lookup__program",
        )
        logger.info(
            f"Handling  feedbacks to specific program: {batch_start} of {feedback_objects_for_specific_program_count}"
        )
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        old_grievance_tickets_to_update = []
        old_feedbacks_to_update = []
        new_feedback_messages_to_create = []

        for feedback_obj in feedback_objects_for_specific_program_batch:
            household_representation = None
            individual_representation = None
            if feedback_obj.program:
                program = feedback_obj.program
                if feedback_obj.household_lookup:
                    household_representation = get_household_representation_per_program_by_old_household_id(
                        program=program,
                        old_household_id=feedback_obj.household_lookup,
                    )
                if feedback_obj.individual_lookup:
                    individual_representation = get_individual_representation_per_program_by_old_individual_id(
                        program=program,
                        old_individual_id=feedback_obj.individual_lookup,
                    )
            elif feedback_obj.household_lookup:
                if household_representation := feedback_obj.household_lookup.copied_to.first():
                    program = household_representation.program
                    if feedback_obj.individual_lookup:
                        individual_representation = get_individual_representation_per_program_by_old_individual_id(
                            program=program,
                            old_individual_id=feedback_obj.individual_lookup,
                        )
            elif feedback_obj.individual_lookup:
                if individual_representation := feedback_obj.individual_lookup.copied_to.first():
                    program = individual_representation.program
            else:
                program = None

            if program:
                (
                    feedback_copy,
                    grievance_ticket_data,
                    notes_to_create,
                    documents_to_create,
                    messages_to_create,
                ) = copy_feedback(feedback_obj, program, household_representation, individual_representation)
                objects_to_create_dict["notes"].extend(notes_to_create)
                objects_to_create_dict["documents"].extend(documents_to_create)
                if grievance_ticket_data:
                    objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                objects_to_create_dict["tickets"].append(feedback_copy)
                new_feedback_messages_to_create.extend(messages_to_create)

                feedback_obj.is_migration_handled = True
                old_feedbacks_to_update.append(feedback_obj)
                if linked_grievance := feedback_obj.linked_grievance:
                    linked_grievance.is_migration_handled = True
                    old_grievance_tickets_to_update.append(linked_grievance)

        handle_bulk_create_paginated_data(old_grievance_tickets_to_update, objects_to_create_dict, Feedback)
        FeedbackMessage.objects.bulk_create(new_feedback_messages_to_create)
        Feedback.objects.bulk_update(old_feedbacks_to_update, ["is_migration_handled", "migrated_at"])


def handle_active_feedback(business_area: Optional[BusinessArea] = None) -> None:
    if business_area:
        filter_kwargs = {"business_area": business_area}
    else:
        filter_kwargs = {}
    active_feedback_objects = (
        Feedback.original_and_repr_objects.select_related(
            "linked_grievance",
            "program",
            "household_lookup",
            "individual_lookup",
            "household_lookup__program",
            "individual_lookup__program",
        )
        .prefetch_related(
            "feedback_messages",
        )
        .filter(
            (Q(linked_grievance__isnull=True) | ~Q(linked_grievance__status=GrievanceTicket.STATUS_CLOSED))
            & Q(program__isnull=True)
            & Q(is_original=True)
            & Q(is_migration_handled=False)
        )
        .filter(**filter_kwargs)
        .distinct()
    )
    logger.info("Handle Feedback objects without program and without closed grievance ticket")

    active_feedback_objects_ids = list(active_feedback_objects.values_list("pk", flat=True))
    active_feedback_objects_count = len(active_feedback_objects_ids)
    logger.info(f"Active Feedback objects to handle: {active_feedback_objects_count}")
    for batch_start in range(0, active_feedback_objects_count, BATCH_SIZE):
        active_feedback_objects_batched_ids = active_feedback_objects_ids[batch_start : batch_start + BATCH_SIZE]
        active_feedback_objects_batch = Feedback.original_and_repr_objects.filter(
            id__in=active_feedback_objects_batched_ids
        ).select_related(
            "linked_grievance",
            "program",
            "household_lookup",
            "individual_lookup",
            "household_lookup__program",
            "individual_lookup__program",
        )
        logger.info(f"Handling  active feedbacks: {batch_start} of {active_feedback_objects_count}")
        objects_to_create_dict = {
            "notes": [],
            "documents": [],
            "grievance_tickets": [],
            "tickets": [],
        }
        old_grievance_tickets_to_update = []
        old_feedbacks_to_update = []
        new_feedback_messages_to_create = []

        for feedback_obj in active_feedback_objects_batch:
            if feedback_obj.individual_lookup:
                individual_representations = feedback_obj.individual_lookup.copied_to.all()
            else:
                individual_representations = Individual.objects.none()
            if feedback_obj.household_lookup:
                household_representations = feedback_obj.household_lookup.copied_to.all()
            else:
                household_representations = Household.objects.none()
            if individual_representations or household_representations:
                household_programs = household_representations.values_list("program", flat=True).distinct()
                individual_programs = individual_representations.values_list("program", flat=True).distinct()

                all_programs = (
                    Program.objects.filter(Q(id__in=household_programs) | Q(id__in=individual_programs))
                    .distinct()
                    .iterator()
                )

                for program in all_programs:
                    (
                        feedback_copy,
                        grievance_ticket_data,
                        notes_to_create,
                        documents_to_create,
                        messages_to_create,
                    ) = copy_feedback(feedback_obj, program)

                    objects_to_create_dict["notes"].extend(notes_to_create)
                    objects_to_create_dict["documents"].extend(documents_to_create)
                    if grievance_ticket_data:
                        objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                    objects_to_create_dict["tickets"].append(feedback_copy)
                    new_feedback_messages_to_create.extend(messages_to_create)

                feedback_obj.is_migration_handled = True
                old_feedbacks_to_update.append(feedback_obj)

                if linked_grievance := feedback_obj.linked_grievance:
                    linked_grievance.is_migration_handled = True
                    old_grievance_tickets_to_update.append(linked_grievance)

        handle_bulk_create_paginated_data(old_grievance_tickets_to_update, objects_to_create_dict, Feedback)
        FeedbackMessage.objects.bulk_create(new_feedback_messages_to_create)
        Feedback.objects.bulk_update(old_feedbacks_to_update, ["is_migration_handled", "migrated_at"])


def copy_feedback(
    feedback_obj: Feedback,
    program: Program,
    household_representation: Optional[Household] = None,
    individual_representation: Optional[Individual] = None,
) -> tuple:
    feedback_copy = copy.deepcopy(feedback_obj)
    if not household_representation and feedback_copy.household_lookup:
        household_representation = get_household_representation_per_program_by_old_household_id(
            program=program,
            old_household_id=feedback_copy.household_lookup,
        )
    feedback_copy.household_lookup = household_representation

    if not individual_representation and feedback_copy.individual_lookup:
        individual_representation = get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=feedback_copy.individual_lookup,
        )
    feedback_copy.individual_lookup = individual_representation

    feedback_copy.pk = None
    feedback_copy.is_original = False
    feedback_copy.copied_from = feedback_obj
    feedback_copy.unicef_id = None
    if feedback_copy.linked_grievance:
        grievance_ticket_data, notes_to_create, documents_to_create = copy_grievance_ticket(
            feedback_copy, program, feedback_obj, related_grievance_field="linked_grievance"
        )
    else:
        grievance_ticket_data, notes_to_create, documents_to_create = {}, [], []

    feedback_copy.program = program
    messages_to_create = []
    for message in feedback_obj.feedback_messages.all():
        message_copy = copy.deepcopy(message)
        message_copy.pk = None
        message_copy.feedback = feedback_copy
        messages_to_create.append(message_copy)

    return feedback_copy, grievance_ticket_data, notes_to_create, documents_to_create, messages_to_create


def copy_grievance_ticket(
    ticket_copy: Any,
    program: Program,
    original_ticket: Any,
    related_grievance_field: str = "ticket",
) -> tuple:
    grievance_ticket = getattr(ticket_copy, related_grievance_field)
    original_grievance_ticket_id = grievance_ticket.pk
    grievance_ticket.pk = None
    grievance_ticket.unicef_id = None
    grievance_ticket.is_original = False
    grievance_ticket.copied_from_id = original_grievance_ticket_id

    grievance_ticket_data = {
        "grievance_ticket": grievance_ticket,
        "program": program,
    }
    notes_to_create = []
    for note in getattr(original_ticket, related_grievance_field).ticket_notes.all():
        note.pk = None
        note.ticket = grievance_ticket
        notes_to_create.append(note)

    documents_to_create = []
    for document in getattr(original_ticket, related_grievance_field).support_documents.all():
        document.pk = None
        document.grievance_ticket = grievance_ticket
        documents_to_create.append(document)

    setattr(ticket_copy, related_grievance_field, grievance_ticket)

    return grievance_ticket_data, notes_to_create, documents_to_create


def migrate_linked_tickets(business_area: Optional[BusinessArea] = None) -> None:
    logger.info(f"Handling linked tickets for business area: {business_area}")

    filter_params = {}
    if business_area:
        filter_params["business_area"] = business_area

    tickets_representations_ids = list(
        GrievanceTicket.objects.filter(**filter_params, is_original=False).values_list("id", flat=True)
    )
    tickets_representations_count = len(tickets_representations_ids)
    logger.info(f"Tickets representations to handle: {tickets_representations_count}")
    for batch_start in range(0, tickets_representations_count, BATCH_SIZE):
        batched_ids = tickets_representations_ids[batch_start : batch_start + BATCH_SIZE]
        tickets_representations = GrievanceTicket.objects.filter(id__in=batched_ids).select_related("copied_from")
        # Link all linked_tickets representations with current ticket_representation
        linked_tickets_to_create = []
        for ticket_representation in tickets_representations:
            original_ticket = ticket_representation.copied_from
            linked_tickets_representations = GrievanceTicket.objects.filter(
                copied_from__linked_tickets__in=[original_ticket]
            ).distinct()
            for linked_ticket_representation in linked_tickets_representations:
                linked_tickets_to_create.extend(
                    [
                        GrievanceTicketThrough(
                            main_ticket=ticket_representation,
                            linked_ticket=linked_ticket_representation,
                        ),
                        GrievanceTicketThrough(
                            main_ticket=linked_ticket_representation,
                            linked_ticket=ticket_representation,
                        ),
                    ]
                )
            # Link all representations of the same ticket with current representation
            for ticket_other_representation in original_ticket.copied_to.all():
                if ticket_other_representation.pk != ticket_representation.pk:
                    linked_tickets_to_create.extend(
                        [
                            GrievanceTicketThrough(
                                main_ticket=ticket_representation,
                                linked_ticket=ticket_other_representation,
                            ),
                            GrievanceTicketThrough(
                                main_ticket=ticket_other_representation,
                                linked_ticket=ticket_representation,
                            ),
                        ]
                    )

        GrievanceTicketThrough.objects.bulk_create(linked_tickets_to_create, ignore_conflicts=True)


def handle_grievance_ticket_data_creation(grievance_ticket_data: list) -> None:
    """
    Function that bulk creates grievance tickets, add their linked tickets and programs relation.
    grievance_ticket_data consists of 3 keys:
    - grievance_ticket: GrievanceTicket object list
    - program: Program for which GrievanceTicket is created ( in many-to-many relation "programs")
    """
    GrievanceTicketProgram = GrievanceTicket.programs.through

    grievance_tickets = [gt["grievance_ticket"] for gt in grievance_ticket_data]
    grievance_tickets_program = []
    for grievance_ticket in grievance_ticket_data:
        program_id = (
            grievance_ticket["program"].pk
            if isinstance(grievance_ticket["program"], Program)
            else grievance_ticket["program"]
        )
        grievance_tickets_program.append(
            GrievanceTicketProgram(grievanceticket=grievance_ticket["grievance_ticket"], program_id=program_id)
        )

    GrievanceTicket.objects.bulk_create(grievance_tickets)
    GrievanceTicketProgram.objects.bulk_create(grievance_tickets_program, ignore_conflicts=True)


def handle_bulk_create_paginated_data(
    old_grievance_tickets_to_update: list, objects_to_create_dict: dict, model: Any
) -> None:
    handle_grievance_ticket_data_creation(objects_to_create_dict["grievance_tickets"])
    TicketNote.objects.bulk_create(objects_to_create_dict["notes"])
    GrievanceDocument.objects.bulk_create(objects_to_create_dict["documents"])
    GrievanceTicket.objects.bulk_update(old_grievance_tickets_to_update, ["is_migration_handled", "migrated_at"])
    model.objects.bulk_create(objects_to_create_dict["tickets"])


def handle_bulk_update_representations_household_unicef_id(query: QuerySet, model: Any) -> None:
    related_name = ticket_grievance_ticket_field_name_mapping[model]
    GrievanceTicket.objects.filter(**{f"{related_name}__in": query}).update(
        household_unicef_id=Subquery(
            GrievanceTicket.objects.filter(pk=OuterRef("pk")).values(f"{related_name}__household__unicef_id")[:1]
        )
    )


def create_void_program(business_area: BusinessArea) -> Program:
    return Program.all_objects.get_or_create(
        name="Storage Program For Non-Program Grievance And Accountability",
        business_area=business_area,
        defaults=dict(
            status=Program.DRAFT,
            start_date=timezone.datetime.min,
            end_date=timezone.datetime.max,
            budget=0,
            frequency_of_payments=Program.ONE_OFF,
            sector=Program.CHILD_PROTECTION,
            scope=Program.SCOPE_FOR_PARTNERS,
            cash_plus=True,
            population_goal=1,
            is_visible=False,
        ),
    )[0]


def handle_non_program_tickets(business_area: Optional[BusinessArea] = None) -> None:
    """
    Handle tickets that are not connected to any program. They should be moved to dummy program.
    Exclude payment-related-tickets that will be handled during sync.
    """
    business_areas = [business_area] if business_area else BusinessArea.objects.all().iterator()
    for business_area in business_areas:
        non_program_query = (
            Q(ticket__business_area=business_area) & Q(ticket__is_migration_handled=False) & Q(ticket__is_original=True)
        )
        non_program_tickets_dict = {
            TicketComplaintDetails: TicketComplaintDetails.objects.filter(
                non_program_query & ~Q(payment_object_id__isnull=False)
            ).order_by("id"),
            TicketSensitiveDetails: TicketSensitiveDetails.objects.filter(
                non_program_query & ~Q(payment_object_id__isnull=False)
            ).order_by("id"),
            TicketPaymentVerificationDetails: TicketPaymentVerificationDetails.objects.filter(
                non_program_query
                & ~(Q(payment_verification__isnull=False) & Q(payment_verification__payment_object_id__isnull=False))
            ).order_by("id"),
            TicketHouseholdDataUpdateDetails: TicketHouseholdDataUpdateDetails.objects.filter(
                non_program_query
            ).order_by("id"),
            TicketIndividualDataUpdateDetails: TicketIndividualDataUpdateDetails.objects.filter(
                non_program_query
            ).order_by("id"),
            TicketAddIndividualDetails: TicketAddIndividualDetails.objects.filter(non_program_query).order_by("id"),
            TicketDeleteIndividualDetails: TicketDeleteIndividualDetails.objects.filter(non_program_query).order_by(
                "id"
            ),
            TicketDeleteHouseholdDetails: TicketDeleteHouseholdDetails.objects.filter(non_program_query).order_by("id"),
            TicketSystemFlaggingDetails: TicketSystemFlaggingDetails.objects.filter(non_program_query).order_by("id"),
            TicketPositiveFeedbackDetails: TicketPositiveFeedbackDetails.objects.filter(non_program_query).order_by(
                "id"
            ),
            TicketNegativeFeedbackDetails: TicketNegativeFeedbackDetails.objects.filter(non_program_query).order_by(
                "id"
            ),
            TicketNeedsAdjudicationDetails: TicketNeedsAdjudicationDetails.objects.filter(non_program_query).order_by(
                "id"
            ),
            TicketReferralDetails: TicketReferralDetails.objects.filter(non_program_query).order_by("id"),
        }

        void_program = create_void_program(business_area)  # type: ignore[arg-type]
        for model, query in non_program_tickets_dict.items():
            objects_ids = list(query.values_list("pk", flat=True))
            objects_count = len(objects_ids)
            logger.info(f"Non-program tickets of type {model.__name__} to handle: {objects_count}")
            for batch_start in range(0, objects_count, BATCH_SIZE):
                objects_batched_ids = objects_ids[batch_start : batch_start + BATCH_SIZE]
                objects_batch = model.objects.filter(id__in=objects_batched_ids).select_related("ticket")
                logger.info(f"Handling non-program tickets of type {model.__name__}: {batch_start} of {objects_count}")
                objects_to_create_dict = {
                    "notes": [],
                    "documents": [],
                    "grievance_tickets": [],
                    "tickets": [],
                }
                old_grievance_tickets_to_update = []
                for non_program_ticket in objects_batch:
                    ticket_copy = copy.deepcopy(non_program_ticket)
                    ticket_copy.pk = None
                    non_program_ticket.pk = None
                    grievance_ticket_data, notes_to_create, documents_to_create = copy_grievance_ticket(
                        ticket_copy, void_program, non_program_ticket
                    )

                    objects_to_create_dict["tickets"].append(ticket_copy)
                    objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                    objects_to_create_dict["documents"].extend(documents_to_create)
                    objects_to_create_dict["notes"].extend(notes_to_create)

                    grievance_ticket = non_program_ticket.ticket
                    grievance_ticket.is_migration_handled = True
                    old_grievance_tickets_to_update.append(grievance_ticket)

                handle_bulk_create_paginated_data(old_grievance_tickets_to_update, objects_to_create_dict, model)


def handle_non_program_feedback(business_area: Optional[BusinessArea] = None) -> None:
    """
    Handle feedback that is not connected to any project. They should be moved to dummy program.
    """
    business_areas = [business_area] if business_area else BusinessArea.objects.all().iterator()
    for business_area in business_areas:
        non_program_feedback_objects = Feedback.original_and_repr_objects.filter(
            is_original=True, is_migration_handled=False, business_area=business_area
        )
        if non_program_feedback_objects:
            void_program = create_void_program(business_area)  # type: ignore[arg-type]

            non_program_feedback_objects_ids = list(non_program_feedback_objects.values_list("pk", flat=True))
            non_program_feedback_objects_count = len(non_program_feedback_objects_ids)
            logger.info(f"Non-program feedback objects to handle: {non_program_feedback_objects_count}")
            for batch_start in range(0, non_program_feedback_objects_count, BATCH_SIZE):
                non_program_feedback_objects_batched_ids = non_program_feedback_objects_ids[
                    batch_start : batch_start + BATCH_SIZE
                ]
                non_program_feedback_objects_batch = Feedback.original_and_repr_objects.filter(
                    id__in=non_program_feedback_objects_batched_ids
                ).select_related("linked_grievance")
                logger.info(
                    f"Handling non-program feedback objects: {batch_start} of {non_program_feedback_objects_count}"
                )
                objects_to_create_dict = {
                    "notes": [],
                    "documents": [],
                    "grievance_tickets": [],
                    "tickets": [],
                }
                old_grievance_tickets_to_update = []
                old_feedbacks_to_update = []
                new_feedback_messages_to_create = []

                for feedback in non_program_feedback_objects_batch:
                    (
                        feedback_copy,
                        grievance_ticket_data,
                        notes_to_create,
                        documents_to_create,
                        messages_to_create,
                    ) = copy_feedback(feedback, void_program)
                    objects_to_create_dict["notes"].extend(notes_to_create)
                    objects_to_create_dict["documents"].extend(documents_to_create)
                    if grievance_ticket_data:
                        objects_to_create_dict["grievance_tickets"].append(grievance_ticket_data)
                    objects_to_create_dict["tickets"].append(feedback_copy)
                    new_feedback_messages_to_create.extend(messages_to_create)

                    feedback.is_migration_handled = True
                    old_feedbacks_to_update.append(feedback)

                handle_bulk_create_paginated_data(old_grievance_tickets_to_update, objects_to_create_dict, Feedback)
                FeedbackMessage.objects.bulk_create(new_feedback_messages_to_create)
                Feedback.objects.bulk_update(old_feedbacks_to_update, ["is_migration_handled", "migrated_at"])


def handle_non_program_messages(business_area: Optional[BusinessArea] = None) -> None:
    business_areas = [business_area] if business_area else BusinessArea.objects.all().iterator()
    for business_area in business_areas:
        non_program_messages = Message.original_and_repr_objects.filter(
            is_original=True, business_area=business_area, is_migration_handled=False
        )
        if non_program_messages:
            void_program = create_void_program(business_area)  # type: ignore[arg-type]

            non_program_message_objects_ids = list(non_program_messages.values_list("pk", flat=True))
            non_program_message_objects_count = len(non_program_message_objects_ids)
            logger.info(f"Non-program message objects to handle: {non_program_message_objects_count}")
            for batch_start in range(0, non_program_message_objects_count, BATCH_SIZE):
                non_program_message_objects_batched_ids = non_program_message_objects_ids[
                    batch_start : batch_start + BATCH_SIZE
                ]
                non_program_message_objects_batch = Message.original_and_repr_objects.filter(
                    id__in=non_program_message_objects_batched_ids
                )
                logger.info(
                    f"Handling non-program message objects: {batch_start} of {non_program_message_objects_count}"
                )
                new_messages_to_create = []
                message_household_to_create = []
                old_messages_to_update = []
                for message in non_program_message_objects_batch:
                    message_copy, message_household = copy_message(message, void_program)
                    new_messages_to_create.append(message_copy)
                    message_household_to_create.extend(message_household)
                    message.is_migration_handled = True
                    old_messages_to_update.append(message)
                Message.objects.bulk_create(new_messages_to_create)
                MessageHouseholdRelation = Message.households.through
                MessageHouseholdRelation.objects.bulk_create(message_household_to_create)
                Message.objects.bulk_update(old_messages_to_update, ["is_migration_handled", "migrated_at"])


def handle_role_reassign_data(ticket: Any, program: Program) -> Any:
    """
    role_reassign_data structure:
    {
        role_uuid / "HEAD": {
            "household": household_encoded_id,
            "individual": individual_encoded_id,
            "role": role
        },
        ...
    }
    """

    def retrieve_household_representation(household_from_json: Household, program: Program) -> Optional[Household]:
        if household_from_json_in_program := household_from_json.copied_to.filter(program=program).first():
            encoded_id = encode_id_base64(household_from_json_in_program.id, "Household")
            role_data["household"] = encoded_id
        return household_from_json_in_program

    def retrieve_individual_representation(individual_from_json: Individual, program: Program) -> Optional[Individual]:
        if individual_from_json_in_program := individual_from_json.copied_to.filter(program=program).first():
            encoded_id = encode_id_base64(individual_from_json_in_program.id, "Individual")
            role_data["individual"] = encoded_id
        return individual_from_json_in_program

    def retrieve_role_from_program(role_from_json: IndividualRoleInHousehold, program: Program) -> Optional[Individual]:
        role_household_in_program = role_from_json.household.copied_to.filter(program=program).first()
        role_individual_in_program = role_from_json.individual.copied_to.filter(program=program).first()

        role_from_json_in_program = IndividualRoleInHousehold.objects.filter(
            household=role_household_in_program, individual=role_individual_in_program
        ).first()
        return role_from_json_in_program

    if not ticket.role_reassign_data:
        return ticket

    new_role_reassign_data = {}
    for role_uuid, role_data in ticket.role_reassign_data.items():
        role_data_to_extend = {}

        household_from_json = Household.original_and_repr_objects.filter(
            id=decode_id_string(role_data.get("household"))
        ).first()
        # Fetch correct household representation from JSON
        household_from_json_in_program = (
            retrieve_household_representation(household_from_json, program) if household_from_json else None
        )

        individual_from_json = Individual.original_and_repr_objects.filter(
            id=decode_id_string(role_data.get("individual"))
        ).first()
        # Fetch correct individual representation from JSON
        individual_from_json_in_program = (
            retrieve_individual_representation(individual_from_json, program) if individual_from_json else None
        )

        if household_from_json_in_program and individual_from_json_in_program:
            if role_uuid == "HEAD":
                role_data_to_extend["HEAD"] = role_data
            else:
                role_from_json = IndividualRoleInHousehold.original_and_repr_objects.filter(id=role_uuid).first()
                # Fetch correct role representation from JSON
                role_from_json_in_program = (
                    retrieve_role_from_program(role_from_json, program) if role_from_json else None
                )
                if role_from_json_in_program:
                    role_data_to_extend[str(role_from_json_in_program.id)] = role_data

        if role_data_to_extend:
            new_role_reassign_data.update(role_data_to_extend)

    ticket.role_reassign_data = new_role_reassign_data
    return ticket


def handle_extra_data(ticket: Any, program: Program) -> Any:
    """
    extra_data structure:
    {
        "golden_records": [
            {
                "dob": date_of_birth,
                "full_name": full_name,
                "hit_id": hit_id,
                "location": location,
                "proximity_to_score": proximity_to_score,
                "score": score
            },
            ...
        ],
        "possible_duplicate": [
            {
                "dob": date_of_birth,
                "full_name": full_name,
                "hit_id":  hit_id,
                "location": location,
                "proximity_to_score": proximity_to_score,
                "score": score
            },
            ...
        ]
    }
    """

    if not ticket.extra_data:
        return ticket

    for list_data in ticket.extra_data.values():
        for ind_data in list_data:
            id_found = False
            hit_from_json = Individual.original_and_repr_objects.filter(id=ind_data.get("hit_id")).first()
            # Fetch correct individual representation from JSON
            if hit_from_json:
                hit_from_json_in_program = hit_from_json.copied_to.filter(program=program).first()
                if hit_from_json_in_program:
                    id_found = True
                    ind_data["hit_id"] = str(hit_from_json_in_program.id)
            if id_found is False:
                list_data.remove(ind_data)

    # ticket.save()
    return ticket


def handle_individual_data(
    ticket: TicketIndividualDataUpdateDetails, program: Program
) -> TicketIndividualDataUpdateDetails:
    """
    individual_data consists of multiple values, but only some have ids.
    These are: [documents/identities/payment_channels]_to_remove and _to_edit.
    Structure of individual_data:
    {
        "_to_remove": [
            {
                "approve_status": bool,
                "value": "base64_id_of_object_to_remove"
            }
        ]
        "_to_edit": [
            {
                "approve_status": bool,
                "previous_value": {
                    "id": base64_object_id,
                    (if not document)
                    "individual": base64_individual_id,
                    **other_object_specific_fields
                },
                "value": {
                    "id": base64_object_id(the same as the one above),
                    (if not document)
                    "individual": base64_individual_id,
                    **other_object_specific_fields
                }
            }
        ],
        also for _to_remove objects there are corresponding previous_[documents/identities/payment_channels].
        {
            "base64_object_id": {
                "id": same as base64_object_id(same as value in _to_remove),
                "individual" base64_document_individual_id,
                **object specific data
            }
        }
    }
    """
    individual = ticket.individual
    individual_in_program = individual.copied_to.filter(program=program).first()
    if not individual_in_program:
        return ticket

    encoded_individual_id = encode_id_base64(individual_in_program.id, "Individual")
    individual_data = ticket.individual_data
    if not individual_data:
        return ticket

    for model in (Document, IndividualIdentity, BankAccountInfo):
        IndividualDataObjectsToEditHandler(
            individual_data,
            individual_in_program,
            model,
            encoded_individual_id,
        ).handle_objects_to_edit()
        IndividualDataObjectsToRemoveHandler(
            individual_data,
            individual_in_program,
            model,
            encoded_individual_id,
        ).handle_objects_to_remove()

    ticket.individual_data = individual_data
    # ticket.save(update_fields=["individual_data"])
    return ticket


class IndividualDataObjectsToRemoveHandler:
    def __init__(
        self,
        individual_data: dict,
        individual_in_program: Individual,
        model: Any,
        encoded_individual_id: Optional[str],
    ) -> None:
        self.individual_data = individual_data
        self.model = model
        self.objects_to_remove_string, self.previous_objects_string = self.object_specific_update_fields()
        self.individual_in_program = individual_in_program
        self.encoded_individual_id = encoded_individual_id

    def object_specific_update_fields(self) -> tuple[str, str]:
        model_related_string = {
            Document: "documents",
            IndividualIdentity: "identities",
            BankAccountInfo: "payment_channels",
        }[self.model]
        return f"{model_related_string}_to_remove", f"previous_{model_related_string}"

    def object_specific_get_fields(self, previous_object: dict) -> dict:
        if self.model == IndividualIdentity:
            return {
                "country__iso_code3": previous_object.get("country"),
                "number": previous_object.get("number"),
                "partner__name": previous_object.get("partner"),
            }
        elif self.model == Document:
            return {
                "document_number": previous_object.get("document_number"),
                "country__iso_code3": previous_object.get("country"),
                "type__key": previous_object.get("key"),
            }
        else:
            return {
                "bank_name": previous_object.get("bank_name"),
                "bank_account_number": previous_object.get("bank_account_number"),
            }

    def handle_individual_data_update(
        self,
        index: int,
        object_in_program_encoded_id: Optional[str],
        object_to_remove_id: str,
    ) -> None:
        self.individual_data[self.objects_to_remove_string][index]["value"] = object_in_program_encoded_id
        self.individual_data[self.previous_objects_string][object_to_remove_id]["id"] = object_in_program_encoded_id
        self.individual_data[self.previous_objects_string][object_to_remove_id][
            "individual"
        ] = self.encoded_individual_id
        if object_in_program_encoded_id != object_to_remove_id:
            self.individual_data[self.previous_objects_string][object_in_program_encoded_id] = copy.deepcopy(
                self.individual_data[self.previous_objects_string][object_to_remove_id]
            )
            del self.individual_data[self.previous_objects_string][object_to_remove_id]

    def handle_objects_to_remove(self) -> None:
        for index, object_to_remove in enumerate(self.individual_data.get(self.objects_to_remove_string, [])):
            object_to_remove_id = object_to_remove.get("value")
            previous_object = self.individual_data.get(self.previous_objects_string, {}).get(object_to_remove_id, {})
            if not previous_object:
                continue
            object_in_program = self.model.objects.filter(
                individual=self.individual_in_program,
                **self.object_specific_get_fields(previous_object),
            ).first()
            if object_in_program:
                object_in_program_encoded_id = encode_id_base64(object_in_program.id, self.model.__name__)
                self.handle_individual_data_update(
                    index,
                    object_in_program_encoded_id,
                    object_to_remove_id,
                )


class IndividualDataObjectsToEditHandler:
    def __init__(
        self,
        individual_data: dict,
        individual_in_program: Individual,
        model: Any,
        encoded_individual_id: Optional[str],
    ) -> None:
        self.individual_data = individual_data
        self.model = model
        self.objects_to_edit_string = self.object_specific_edit_fields()
        self.individual_in_program = individual_in_program
        self.encoded_individual_id = encoded_individual_id

    def object_specific_edit_fields(self) -> str:
        model_related_string = {
            Document: "documents",
            IndividualIdentity: "identities",
            BankAccountInfo: "payment_channels",
        }[self.model]
        return f"{model_related_string}_to_edit"

    def get_object_specific_fields(self, previous_value: dict) -> dict:
        if self.model == IndividualIdentity:
            return {
                "country__iso_code3": previous_value.get("country"),
                "number": previous_value.get("number"),
                "partner__name": previous_value.get("partner"),
            }
        elif self.model == Document:
            return {
                "document_number": previous_value.get("number"),
                "country__iso_code3": previous_value.get("country"),
            }
        else:
            return {
                "bank_name": previous_value.get("bank_name"),
                "bank_account_number": previous_value.get("bank_account_number"),
            }

    def handle_objects_to_edit(self) -> None:
        for index, object_to_edit in enumerate(self.individual_data.get(self.objects_to_edit_string, [])):
            object_in_program = self.model.objects.filter(
                individual=self.individual_in_program,
                **self.get_object_specific_fields(object_to_edit.get("previous_value", {})),
            ).first()
            if not object_in_program:
                object_in_program = self.model.objects.filter(
                    individual=self.individual_in_program,
                    **self.get_object_specific_fields(object_to_edit.get("value", {})),
                ).first()
                if not object_in_program:
                    continue
            object_in_program_encoded_id = encode_id_base64(object_in_program.id, self.model.__name__)
            self.individual_data[self.objects_to_edit_string][index]["value"]["id"] = object_in_program_encoded_id
            self.individual_data[self.objects_to_edit_string][index]["previous_value"][
                "id"
            ] = object_in_program_encoded_id
            if self.model != Document:
                self.individual_data[self.objects_to_edit_string][index]["value"][
                    "individual"
                ] = self.encoded_individual_id
                self.individual_data[self.objects_to_edit_string][index]["previous_value"][
                    "individual"
                ] = self.encoded_individual_id


def handle_payment_related_tickets(business_area: Optional[BusinessArea] = None) -> None:
    """
    Assign grievance tickets to representations. Applied for tickets connected to specific payment.
    Handle TicketComplaintDetails, TicketSensitiveDetails, TicketPaymentVerificationDetails with related payment_obj
    """
    if business_area:
        filter_kwargs = {"ticket__business_area": business_area}
    else:
        filter_kwargs = {}
    # Fetch all objects of TicketComplaintDetails and TicketSensitiveDetails with non-null payment_obj
    complaint_tickets_with_payments = TicketComplaintDetails.objects.select_related(
        "household",
        "individual",
    ).filter(
        payment_object_id__isnull=False, ticket__is_original=True, ticket__is_migration_handled=False, **filter_kwargs
    )
    sensitive_tickets_with_payments = TicketSensitiveDetails.objects.select_related(
        "household",
        "individual",
    ).filter(
        payment_object_id__isnull=False, ticket__is_original=True, ticket__is_migration_handled=False, **filter_kwargs
    )

    complaint_and_sensitive_details_tickets = chain(complaint_tickets_with_payments, sensitive_tickets_with_payments)

    # Update household and individual fields based on payment_obj for TicketComplaintDetails and TicketSensitiveDetails
    for ticket in complaint_and_sensitive_details_tickets:
        household, individual, program = get_program_and_representations_for_payment(ticket)
        ticket.household = household
        ticket.individual = individual
        if program:
            ticket.ticket.programs.set([program])

    # Perform a bulk update for the household and individual fields of TicketComplaintDetails and TicketSensitiveDetails
    TicketComplaintDetails.objects.bulk_update(complaint_tickets_with_payments, ["household", "individual"])
    TicketSensitiveDetails.objects.bulk_update(sensitive_tickets_with_payments, ["household", "individual"])

    # Update household_unicef_id for all related GrievanceTickets
    # Fetch the GrievanceTickets related to the updated objects
    grievance_tickets = GrievanceTicket.default_for_migrations_fix.filter(
        Q(complaint_ticket_details__in=complaint_tickets_with_payments)
        | Q(sensitive_ticket_details__in=sensitive_tickets_with_payments)
    ).distinct()
    # Update household_unicef_id for each GrievanceTicket using bulk_update
    for grievance_ticket in grievance_tickets:
        related_ticket = getattr(grievance_ticket, "complaint_ticket_details", None) or getattr(
            grievance_ticket, "sensitive_ticket_details", None
        )
        household_unicef_id = getattr(related_ticket.household, "unicef_id", None)
        grievance_ticket.household_unicef_id = household_unicef_id

    GrievanceTicket.objects.bulk_update(grievance_tickets, ["household_unicef_id"])

    # Update programs for TicketPaymentVerificationDetails with payment_obj
    payment_verification_tickets = (
        TicketPaymentVerificationDetails.objects.select_related(
            "payment_verification",
        )
        .filter(
            payment_verification__isnull=False,
            payment_verification__payment_object_id__isnull=False,
            ticket__is_original=True,
            ticket__is_migration_handled=False,
            **filter_kwargs,
        )
        .distinct()
    )
    for payment_verification_ticket in payment_verification_tickets:
        payment_obj = payment_verification_ticket.payment_verification.payment_obj
        if isinstance(payment_obj, Payment):
            program = payment_obj.parent.target_population.program
        elif isinstance(payment_obj, PaymentRecord):
            program = payment_obj.target_population.program
        else:
            program = None
        if program:
            payment_verification_ticket.ticket.programs.set([program])

    GrievanceTicket.default_for_migrations_fix.filter(
        Q(complaint_ticket_details__in=complaint_tickets_with_payments)
        | Q(sensitive_ticket_details__in=sensitive_tickets_with_payments)
        | Q(payment_verification_ticket_details__in=payment_verification_tickets)
    ).update(is_original=False, is_migration_handled=True)


def get_program_and_representations_for_payment(ticket: Union[TicketComplaintDetails, TicketSensitiveDetails]) -> tuple:
    if isinstance(ticket.payment_obj, Payment):
        program = ticket.payment_obj.parent.target_population.program
    elif isinstance(ticket.payment_obj, PaymentRecord):
        program = ticket.payment_obj.target_population.program
    else:
        program = None
    household_representation = (
        get_household_representation_per_program_by_old_household_id(program=program, old_household_id=ticket.household)
        if ticket.household
        else None
    )
    individual_representation = (
        get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=ticket.individual,
        )
        if ticket.individual
        else None
    )
    return household_representation, individual_representation, program
