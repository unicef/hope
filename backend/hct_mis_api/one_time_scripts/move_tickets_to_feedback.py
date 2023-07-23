import logging
from typing import Type

from django.core.paginator import Paginator

from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.grievance.models import (
    TicketNegativeFeedbackDetails,
    TicketPositiveFeedbackDetails,
)

logger = logging.getLogger(__name__)


def move_tickets_to_feedback() -> None:
    for ticket_type in (TicketPositiveFeedbackDetails, TicketNegativeFeedbackDetails):
        move_ticket_model_to_feedback(ticket_type)
        delete_moved_to_feedback_tickets(ticket_type)


def move_ticket_model_to_feedback(model_type: Type[object], batch_size: int = 1000) -> None:
    queryset = TicketPositiveFeedbackDetails.objects.all().order_by("created_at").select_related("ticket")
    paginator = Paginator(queryset, batch_size)
    pages = queryset.count() // batch_size + 1

    issue_type = (
        Feedback.POSITIVE_FEEDBACK if model_type == TicketPositiveFeedbackDetails else Feedback.NEGATIVE_FEEDBACK
    )
    try:
        for page_number in paginator.page_range:
            feedbacks_to_create = []
            logger.info(f"Migration {page_number}/{pages} page")
            page = paginator.page(page_number)
            for obj in page.object_list:
                feedbacks_to_create.append(
                    Feedback(
                        created_at=obj.created_at,
                        household_lookup_id=obj.household.id,
                        individual_lookup_id=obj.individual.id,
                        business_area_id=obj.ticket.business_area.id,
                        issue_type=issue_type,
                        description=obj.ticket.description,
                        admin2_id=obj.ticket.admin2.id,
                        language=obj.ticket.language,
                        area=obj.ticket.area,
                        consent=obj.ticket.consent,
                        comments=obj.ticket.comments,
                        program_id=obj.ticket.programme.id,
                        created_by_id=obj.ticket.created_by.id,
                        linked_grievance_id=obj.ticket.id,
                    )
                )
            Feedback.objects.bulk_create(feedbacks_to_create)
    except Exception:
        logger.error("Migrating tickets to feedback failed")
        raise
    logger.info(f"Migration of {model_type.__name__} succeeded")


def delete_moved_to_feedback_tickets(model_type: Type[object], batch_size: int = 1000) -> None:
    queryset_ids = Feedback.objects.values_list("linked_grievance_id", flat=True)
    i, pages = 0, queryset_ids.count() // batch_size + 1
    try:
        while i <= pages:
            model_type.objects.filter(id__in=list(queryset_ids[i * pages : (i + 1) * pages]))
    except Exception:
        logger.error("Deleting migrated tickets failed")
        raise
