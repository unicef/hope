from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import BusinessAreaFactory, GrievanceTicketFactory, UserFactory
from hope.apps.grievance.celery_tasks import (
    bulk_assign_notifications_async_task,
    bulk_assign_notifications_async_task_action,
)
from hope.apps.grievance.constants import (
    PRIORITY_HIGH,
    PRIORITY_NOT_SET,
    URGENCY_NOT_SET,
    URGENCY_VERY_URGENT,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification
from hope.apps.grievance.services.bulk_action_service import BulkActionService
from hope.models import BusinessArea, User

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def users() -> dict[str, User]:
    return {
        "user": UserFactory(first_name="user"),
        "user_two": UserFactory(first_name="user_two"),
    }


@pytest.fixture
def grievance_context(business_area: BusinessArea, users: dict[str, User]) -> dict[str, Any]:
    user = users["user"]
    user_two = users["user_two"]
    grievance_ticket1 = GrievanceTicketFactory(
        description="Test 1",
        assigned_to=user,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        language="PL",
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        created_by=user,
        business_area=business_area,
    )
    grievance_ticket2 = GrievanceTicketFactory(
        description="Test 2",
        assigned_to=user,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        language="PL",
        status=GrievanceTicket.STATUS_NEW,
        created_by=user,
        business_area=business_area,
    )
    grievance_ticket3 = GrievanceTicketFactory(
        description="Test 3",
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        language="PL",
        status=GrievanceTicket.STATUS_NEW,
        created_by=user,
        business_area=business_area,
    )
    grievance_ticket4 = GrievanceTicketFactory(
        description="Test 4",
        assigned_to=user_two,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        language="PL",
        status=GrievanceTicket.STATUS_NEW,
        created_by=user,
        business_area=business_area,
    )
    return {
        "users": users,
        "business_area": business_area,
        "grievance_tickets": [
            grievance_ticket1,
            grievance_ticket2,
            grievance_ticket3,
            grievance_ticket4,
        ],
    }


@pytest.fixture
def closed_ticket(business_area: BusinessArea, users: dict[str, User]) -> GrievanceTicket:
    user = users["user"]
    return GrievanceTicketFactory(
        description="Closed ticket",
        assigned_to=user,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        language="PL",
        status=GrievanceTicket.STATUS_CLOSED,
        created_by=user,
        business_area=business_area,
    )


def test_bulk_update_assignee(grievance_context: dict[str, Any]) -> None:
    user = grievance_context["users"]["user"]
    user_two = grievance_context["users"]["user_two"]
    business_area = grievance_context["business_area"]
    grievance_ticket1, grievance_ticket2, _, _ = grievance_context["grievance_tickets"]

    assert grievance_ticket1.assigned_to == user
    assert grievance_ticket2.assigned_to == user

    BulkActionService().bulk_assign(
        [grievance_ticket1.id, grievance_ticket2.id],
        user_two.id,
        business_area.slug,
    )

    grievance_ticket1.refresh_from_db()
    grievance_ticket2.refresh_from_db()

    assert grievance_ticket1.assigned_to == user_two
    assert grievance_ticket2.assigned_to == user_two
    assert grievance_ticket1.status == GrievanceTicket.STATUS_FOR_APPROVAL
    assert grievance_ticket2.status == GrievanceTicket.STATUS_ASSIGNED


def test_bulk_update_assignee_enqueues_notification_for_new_assignee(grievance_context: dict[str, Any]) -> None:
    user = grievance_context["users"]["user"]
    user_two = grievance_context["users"]["user_two"]
    business_area = grievance_context["business_area"]
    grievance_ticket1, grievance_ticket2, _, _ = grievance_context["grievance_tickets"]

    with patch("hope.apps.grievance.services.bulk_action_service.bulk_assign_notifications_async_task") as mock_enqueue:
        BulkActionService().bulk_assign(
            [grievance_ticket1.id, grievance_ticket2.id],
            user_two.id,
            business_area.slug,
            action_user=user,
        )

    reassigned_ids, action_user_id = mock_enqueue.call_args.args
    assert set(reassigned_ids) == {grievance_ticket1.id, grievance_ticket2.id}
    assert action_user_id == user.id


def test_bulk_update_assignee_skips_enqueue_when_assignee_unchanged(grievance_context: dict[str, Any]) -> None:
    user = grievance_context["users"]["user"]
    user_two = grievance_context["users"]["user_two"]
    business_area = grievance_context["business_area"]
    _, _, _, grievance_ticket4 = grievance_context["grievance_tickets"]

    assert grievance_ticket4.assigned_to == user_two

    with patch("hope.apps.grievance.services.bulk_action_service.bulk_assign_notifications_async_task") as mock_enqueue:
        BulkActionService().bulk_assign(
            [grievance_ticket4.id],
            user_two.id,
            business_area.slug,
            action_user=user,
        )

    mock_enqueue.assert_not_called()


def test_bulk_assign_notifications_task_action_builds_notification_for_new_assignee(
    grievance_context: dict[str, Any],
) -> None:
    user = grievance_context["users"]["user"]
    user_two = grievance_context["users"]["user_two"]
    grievance_ticket1, grievance_ticket2, _, _ = grievance_context["grievance_tickets"]
    grievance_ticket1.assigned_to = user_two
    grievance_ticket1.save(update_fields=["assigned_to"])
    grievance_ticket2.assigned_to = user_two
    grievance_ticket2.save(update_fields=["assigned_to"])
    job = SimpleNamespace(
        config={
            "ticket_ids": [str(grievance_ticket1.id), str(grievance_ticket2.id)],
            "action_user_id": str(user.id),
        }
    )

    with patch.object(GrievanceNotification, "send_all_notifications") as mock_send:
        bulk_assign_notifications_async_task_action(job)

    sent_notifications = mock_send.call_args.args[0]
    assert {notification.action for notification in sent_notifications} == {
        GrievanceNotification.ACTION_ASSIGNMENT_CHANGED
    }
    assert {notification.grievance_ticket.id for notification in sent_notifications} == {
        grievance_ticket1.id,
        grievance_ticket2.id,
    }
    assert all(notification.user_recipients == [user_two] for notification in sent_notifications)


def test_bulk_assign_notifications_task_action_without_action_user(
    grievance_context: dict[str, Any],
) -> None:
    user_two = grievance_context["users"]["user_two"]
    grievance_ticket1, _, _, _ = grievance_context["grievance_tickets"]
    grievance_ticket1.assigned_to = user_two
    grievance_ticket1.save(update_fields=["assigned_to"])
    job = SimpleNamespace(
        config={
            "ticket_ids": [str(grievance_ticket1.id)],
            "action_user_id": None,
        }
    )

    with patch.object(GrievanceNotification, "send_all_notifications") as mock_send:
        bulk_assign_notifications_async_task_action(job)

    sent_notifications = mock_send.call_args.args[0]
    assert all(notification.extra_data.get("editor") is None for notification in sent_notifications)
    assert all(notification.user_recipients == [user_two] for notification in sent_notifications)


def test_bulk_assign_notifications_task_action_does_not_scale_queries_per_ticket(
    grievance_context: dict[str, Any],
) -> None:
    user = grievance_context["users"]["user"]
    user_two = grievance_context["users"]["user_two"]
    ticket1, ticket2, ticket3, _ = grievance_context["grievance_tickets"]
    for ticket in (ticket1, ticket2, ticket3):
        ticket.assigned_to = user_two
        ticket.save(update_fields=["assigned_to"])
    single_job = SimpleNamespace(config={"ticket_ids": [str(ticket1.id)], "action_user_id": str(user.id)})
    many_job = SimpleNamespace(
        config={
            "ticket_ids": [str(ticket1.id), str(ticket2.id), str(ticket3.id)],
            "action_user_id": str(user.id),
        }
    )

    with patch.object(GrievanceNotification, "send_all_notifications"):
        bulk_assign_notifications_async_task_action(single_job)  # warm up any one-off caches
        with CaptureQueriesContext(connection) as single_ctx:
            bulk_assign_notifications_async_task_action(single_job)
        with CaptureQueriesContext(connection) as many_ctx:
            bulk_assign_notifications_async_task_action(many_job)

    assert len(many_ctx.captured_queries) == len(single_ctx.captured_queries)


def test_bulk_assign_notifications_async_task_queues_job_with_serialized_config(
    grievance_context: dict[str, Any],
) -> None:
    user = grievance_context["users"]["user"]
    grievance_ticket1, grievance_ticket2, _, _ = grievance_context["grievance_tickets"]

    with patch("hope.apps.grievance.celery_tasks.AsyncJob.queue_task") as mock_queue_task:
        bulk_assign_notifications_async_task([grievance_ticket1.id, grievance_ticket2.id], user.id)

    kwargs = mock_queue_task.call_args.kwargs
    assert kwargs["config"]["ticket_ids"] == [str(grievance_ticket1.id), str(grievance_ticket2.id)]
    assert kwargs["config"]["action_user_id"] == str(user.id)
    assert kwargs["owner_id"] == str(user.id)
    assert kwargs["group_key"] == "grievance"
    assert kwargs["action"] == "hope.apps.grievance.celery_tasks.bulk_assign_notifications_async_task_action"


def test_bulk_assign_notifications_async_task_queues_job_without_action_user() -> None:
    with patch("hope.apps.grievance.celery_tasks.AsyncJob.queue_task") as mock_queue_task:
        bulk_assign_notifications_async_task(["11111111-1111-1111-1111-111111111111"], None)

    kwargs = mock_queue_task.call_args.kwargs
    assert kwargs["config"]["action_user_id"] is None
    assert kwargs["owner_id"] is None


def test_bulk_update_priority(grievance_context: dict[str, Any]) -> None:
    business_area = grievance_context["business_area"]
    grievance_ticket1, grievance_ticket2, _, _ = grievance_context["grievance_tickets"]

    assert grievance_ticket1.priority == PRIORITY_NOT_SET
    assert grievance_ticket2.priority == PRIORITY_NOT_SET

    BulkActionService().bulk_set_priority(
        [grievance_ticket1.id, grievance_ticket2.id],
        PRIORITY_HIGH,
        business_area.slug,
    )

    grievance_ticket1.refresh_from_db()
    grievance_ticket2.refresh_from_db()

    assert grievance_ticket1.priority == PRIORITY_HIGH
    assert grievance_ticket2.priority == PRIORITY_HIGH


def test_bulk_update_urgency(grievance_context: dict[str, Any]) -> None:
    business_area = grievance_context["business_area"]
    grievance_ticket1, grievance_ticket2, _, _ = grievance_context["grievance_tickets"]

    assert grievance_ticket1.urgency == URGENCY_NOT_SET
    assert grievance_ticket2.urgency == URGENCY_NOT_SET

    BulkActionService().bulk_set_urgency(
        [grievance_ticket1.id, grievance_ticket2.id],
        URGENCY_VERY_URGENT,
        business_area.slug,
    )

    grievance_ticket1.refresh_from_db()
    grievance_ticket2.refresh_from_db()

    assert grievance_ticket1.urgency == URGENCY_VERY_URGENT
    assert grievance_ticket2.urgency == URGENCY_VERY_URGENT


def test_bulk_add_note(grievance_context: dict[str, Any]) -> None:
    user = grievance_context["users"]["user"]
    business_area = grievance_context["business_area"]
    grievance_ticket1, grievance_ticket2, _, _ = grievance_context["grievance_tickets"]

    assert grievance_ticket1.ticket_notes.count() == 0
    assert grievance_ticket2.ticket_notes.count() == 0

    BulkActionService().bulk_add_note(
        user,
        [grievance_ticket1.id, grievance_ticket2.id],
        "Test note",
        business_area.slug,
    )

    grievance_ticket1.refresh_from_db()
    grievance_ticket2.refresh_from_db()

    assert grievance_ticket1.ticket_notes.count() == 1
    assert grievance_ticket2.ticket_notes.count() == 1
    assert grievance_ticket1.ticket_notes.first().description == "Test note"


def test_bulk_update_assignee_with_closed_ticket_raises(
    closed_ticket: GrievanceTicket, users: dict[str, User], business_area: BusinessArea
) -> None:
    user_two = users["user_two"]

    with pytest.raises(ValidationError, match="Some tickets do not exist or are closed"):
        BulkActionService().bulk_assign([closed_ticket.id], user_two.id, business_area.slug)


def test_bulk_update_priority_with_invalid_priority_raises(business_area: BusinessArea) -> None:
    with pytest.raises(ValidationError, match="Invalid priority"):
        BulkActionService().bulk_set_priority([], 999, business_area.slug)


def test_bulk_update_priority_with_closed_ticket_raises(
    closed_ticket: GrievanceTicket, business_area: BusinessArea
) -> None:
    with pytest.raises(ValidationError, match="Some tickets do not exist or are closed"):
        BulkActionService().bulk_set_priority([closed_ticket.id], PRIORITY_HIGH, business_area.slug)


def test_bulk_update_urgency_with_invalid_urgency_raises(business_area: BusinessArea) -> None:
    with pytest.raises(ValidationError, match="Invalid priority"):
        BulkActionService().bulk_set_urgency([], 999, business_area.slug)


def test_bulk_update_urgency_with_closed_ticket_raises(
    closed_ticket: GrievanceTicket, business_area: BusinessArea
) -> None:
    with pytest.raises(ValidationError, match="Some tickets do not exist or are closed"):
        BulkActionService().bulk_set_urgency([closed_ticket.id], URGENCY_VERY_URGENT, business_area.slug)


def test_bulk_add_note_with_closed_ticket_raises(
    closed_ticket: GrievanceTicket, users: dict[str, User], business_area: BusinessArea
) -> None:
    user = users["user"]

    with pytest.raises(ValidationError, match="Some tickets do not exist, or are closed"):
        BulkActionService().bulk_add_note(user, [closed_ticket.id], "Test note", business_area.slug)
