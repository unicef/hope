import logging

from django.db.models import Case, F, Q, Value, When

from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.grievance.models import GrievanceTicket

logger = logging.getLogger(__name__)


def assign_program_to_grievance_tickets() -> None:
    BATCH_SIZE = 1000
    annotation = Case(
        When(
            Q(complaint_ticket_details__household__isnull=False),
            then=F("complaint_ticket_details__household__program__id"),
        ),
        When(
            Q(complaint_ticket_details__individual__isnull=False),
            then=F("complaint_ticket_details__individual__program__id"),
        ),
        When(
            Q(sensitive_ticket_details__household__isnull=False),
            then=F("sensitive_ticket_details__household__program__id"),
        ),
        When(
            Q(sensitive_ticket_details__individual__isnull=False),
            then=F("sensitive_ticket_details__individual__program__id"),
        ),
        When(
            Q(household_data_update_ticket_details__household__isnull=False),
            then=F("household_data_update_ticket_details__household__program__id"),
        ),
        When(
            Q(add_individual_ticket_details__household__isnull=False),
            then=F("add_individual_ticket_details__household__program__id"),
        ),
        When(
            Q(delete_household_ticket_details__household__isnull=False),
            then=F("delete_household_ticket_details__household__program__id"),
        ),
        When(
            Q(individual_data_update_ticket_details__individual__isnull=False),
            then=F("individual_data_update_ticket_details__individual__program__id"),
        ),
        When(
            Q(delete_individual_ticket_details__individual__isnull=False),
            then=F("delete_individual_ticket_details__individual__program__id"),
        ),
        When(
            Q(referral_ticket_details__household__isnull=False),
            then=F("referral_ticket_details__household__program__id"),
        ),
        When(
            Q(referral_ticket_details__individual__isnull=False),
            then=F("referral_ticket_details__individual__program__id"),
        ),
        default=Value(None),
    )
    grievance_tickets = (
        GrievanceTicket.objects.filter(programs__isnull=True)
        .annotate(
            program=annotation,
        )
        .filter(program__isnull=False)
    )
    GrievanceTicketProgramThrough = GrievanceTicket.programs.through

    grievance_tickets_count = grievance_tickets.count()
    grievance_tickets_ids = list(grievance_tickets.values_list("id", flat=True))

    for batch_start in range(0, grievance_tickets_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logger.info(f"Handling {batch_start} - {batch_end}/{grievance_tickets_count} Grievance Tickets")

        grievance_tickets_programs_to_create = []

        for grievance_ticket in GrievanceTicket.objects.filter(
            id__in=grievance_tickets_ids[batch_start:batch_end]
        ).annotate(program=annotation):
            grievance_tickets_programs_to_create.append(
                GrievanceTicketProgramThrough(grievanceticket=grievance_ticket, program_id=grievance_ticket.program)
            )

        GrievanceTicketProgramThrough.objects.bulk_create(grievance_tickets_programs_to_create)


def assign_program_to_feedback() -> None:
    BATCH_SIZE = 1000

    annotation = Case(
        When(
            Q(household_lookup__isnull=False),
            then=F("household_lookup__program"),
        ),
        When(
            Q(individual_lookup__isnull=False),
            then=F("individual_lookup__program"),
        ),
        default=Value(None),
    )

    feedbacks = (
        Feedback.objects.filter(program__isnull=True)
        .exclude(household_lookup__isnull=True, individual_lookup__isnull=True)
        .annotate(
            program_from_data=annotation,
        )
    )

    feedback_ids = list(feedbacks.values_list("id", flat=True))
    feedbacks_count = feedbacks.count()

    for batch_start in range(0, feedbacks_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logger.info(f"Handling {batch_start} - {batch_end}/{feedbacks_count} Feedbacks")

        feedbacks_to_update = []

        for feedback in Feedback.objects.filter(id__in=feedback_ids[batch_start:batch_end]).annotate(
            program_from_data=annotation
        ):
            feedback.program_id = feedback.program_from_data
            feedbacks_to_update.append(feedback)

        Feedback.objects.bulk_update(feedbacks_to_update, ["program_id"])
