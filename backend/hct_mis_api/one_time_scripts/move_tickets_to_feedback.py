import logging
from typing import Type

from django.core.paginator import Paginator

from hct_mis_api.apps.accountability.models import Feedback, FeedbackMessage
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNegativeFeedbackDetails,
    TicketPositiveFeedbackDetails,
)

logger = logging.getLogger(__name__)


def move_tickets_to_feedback() -> None:
    for ticket_type in (TicketPositiveFeedbackDetails, TicketNegativeFeedbackDetails):
        move_ticket_model_to_feedback(ticket_type)
    move_ticket_notes()
    delete_moved_to_feedback_tickets()


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
                # TODO: maybe refactor this one after Paulina's migration for Grievances
                if obj.ticket.programs.all():
                    # create feedback for every program
                    for program in obj.ticket.programs.all():
                        feedbacks_to_create.append(
                            Feedback(
                                created_at=obj.created_at,
                                household_lookup=getattr(obj, "household", None),
                                individual_lookup=getattr(obj, "individual", None),
                                business_area=obj.ticket.business_area,
                                issue_type=issue_type,
                                description=obj.ticket.description,
                                admin2_id=getattr(obj.ticket.admin2, "id", None),
                                language=obj.ticket.language,
                                area=obj.ticket.area,
                                consent=obj.ticket.consent,
                                comments=obj.ticket.comments,
                                program=program,
                                created_by_id=getattr(obj.ticket.created_by, "id", None),
                                linked_grievance_id=obj.ticket.id,
                            )
                        )
                else:
                    feedbacks_to_create.append(
                        Feedback(
                            created_at=obj.created_at,
                            household_lookup=getattr(obj, "household", None),
                            individual_lookup=getattr(obj, "individual", None),
                            business_area=obj.ticket.business_area,
                            issue_type=issue_type,
                            description=obj.ticket.description,
                            admin2_id=getattr(obj.ticket.admin2, "id", None),
                            language=obj.ticket.language,
                            area=obj.ticket.area,
                            consent=obj.ticket.consent,
                            comments=obj.ticket.comments,
                            program=None,
                            created_by_id=getattr(obj.ticket.created_by, "id", None),
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


def move_ticket_notes() -> None:
    logger.info("Feedback messages - started")
    feedbacks_data = Feedback.objects.filter(
        linked_grievance__ticket_notes__isnull=False,
        issue_type__in=[Feedback.POSITIVE_FEEDBACK, Feedback.NEGATIVE_FEEDBACK],
    ).values(
        "id",
        "linked_grievance__ticket_notes__description",
        "linked_grievance__ticket_notes__created_by_id",
        "linked_grievance__ticket_notes__updated_at",
        "linked_grievance__ticket_notes__created_at",
    )

    FeedbackMessage._meta.get_field("created_at").auto_now_add = False

    feedback_messages = []
    for feedback_data in feedbacks_data:
        feedback_messages.append(
            FeedbackMessage(
                feedback_id=feedback_data["id"],
                description=feedback_data["linked_grievance__ticket_notes__description"],
                created_by_id=feedback_data["linked_grievance__ticket_notes__created_by_id"],
                created_at=feedback_data["linked_grievance__ticket_notes__created_at"],
                updated_at=feedback_data["linked_grievance__ticket_notes__updated_at"],
            )
        )
    logger.info(f"Creating {len(feedback_messages)} feedback messages")
    FeedbackMessage.objects.bulk_create(feedback_messages)
    FeedbackMessage._meta.get_field("created_at").auto_now_add = True
    logger.info("Feedback messages - finished")


def delete_moved_to_feedback_tickets() -> None:
    ticket_ids = Feedback.objects.values("linked_grievance_id")
    result = GrievanceTicket.objects.filter(id__in=ticket_ids).delete()
    logger.info("Removed records")
    logger.info(result)
