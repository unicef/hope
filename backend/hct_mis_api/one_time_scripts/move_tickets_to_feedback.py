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
    queryset = model_type.objects.all().order_by("created_at").select_related("ticket")
    paginator = Paginator(queryset, batch_size)
    pages = queryset.count() // batch_size + 1

    issue_type = (
        Feedback.POSITIVE_FEEDBACK if model_type == TicketPositiveFeedbackDetails else Feedback.NEGATIVE_FEEDBACK
    )

    # Switch off aut_now_add, so newly created feedbacks will have the same created_at timestamp
    Feedback._meta.get_field("created_at").auto_now_add = False
    try:
        for page_number in paginator.page_range:
            feedbacks_to_create = []
            logger.info(f"Migration {page_number}/{pages} page")
            page = paginator.page(page_number)
            for obj in page.object_list:
                feedbacks_to_create.append(
                    Feedback(
                        created_at=obj.created_at,
                        household_lookup=getattr(obj, "household", None),
                        individual_lookup=getattr(obj, "individual", None),
                        business_area=obj.ticket.business_area,
                        issue_type=issue_type,
                        description=obj.ticket.description,
                        admin2_id=obj.ticket.admin2.id,
                        language=obj.ticket.language,
                        area=obj.ticket.area,
                        consent=obj.ticket.consent,
                        comments=obj.ticket.comments,
                        program=obj.ticket.programs.all().first() or None,
                        created_by_id=obj.ticket.created_by.id,
                        linked_grievance_id=obj.ticket.id,
                    )
                )
            Feedback.objects.bulk_create(feedbacks_to_create)
    except Exception:
        logger.error("Migrating tickets to feedback failed")
        raise
    finally:
        # Go back to default settings
        Feedback._meta.get_field("created_at").auto_now_add = True
    logger.info(f"Migration of {model_type.__name__} succeeded")


def delete_moved_to_feedback_tickets(model_type: Type[object], batch_size: int = 1000) -> None:
    if model_type == TicketPositiveFeedbackDetails:
        ticket_ids = Feedback.objects.filter(issue_type=Feedback.POSITIVE_FEEDBACK).values_list(
            "linked_grievance_id", flat=True
        )
    else:
        ticket_ids = Feedback.objects.filter(issue_type=Feedback.NEGATIVE_FEEDBACK).values_list(
            "linked_grievance_id", flat=True
        )
    i, pages = 0, len(ticket_ids) // batch_size + 1
    try:
        while i <= pages:
            model_type.objects.filter(ticket_id__in=list(ticket_ids[i * batch_size : (i + 1) * batch_size])).delete()
            i += 1
    except Exception:
        logger.error("Deleting migrated tickets failed")
        raise
