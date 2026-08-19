from typing import Any

import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import BusinessAreaFactory, GrievanceTicketFactory, UserFactory
from hope.apps.grievance.constants import (
    PRIORITY_HIGH,
    PRIORITY_NOT_SET,
    URGENCY_NOT_SET,
    URGENCY_VERY_URGENT,
)
from hope.apps.grievance.models import GrievanceTicket
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


def test_bulk_update_assignee_stamps_only_the_tickets_that_changed(grievance_context: dict[str, Any]) -> None:
    user = grievance_context["users"]["user"]
    user_two = grievance_context["users"]["user_two"]
    business_area = grievance_context["business_area"]
    grievance_ticket1, _, _, grievance_ticket4 = grievance_context["grievance_tickets"]

    assert grievance_ticket1.assigned_to == user
    assert grievance_ticket4.assigned_to == user_two

    BulkActionService().bulk_assign(
        [grievance_ticket1.id, grievance_ticket4.id],
        user_two.id,
        business_area.slug,
        action_user=user,
    )

    grievance_ticket1.refresh_from_db()
    grievance_ticket4.refresh_from_db()

    assert grievance_ticket1.assigned_at is not None
    assert grievance_ticket1.assigned_by == user
    assert grievance_ticket4.assigned_at is None
    assert grievance_ticket4.assigned_by is None


def test_bulk_update_assignee_leaves_assigned_by_null_without_an_action_user(
    grievance_context: dict[str, Any],
) -> None:
    user_two = grievance_context["users"]["user_two"]
    business_area = grievance_context["business_area"]
    grievance_ticket1, _, _, _ = grievance_context["grievance_tickets"]

    BulkActionService().bulk_assign([grievance_ticket1.id], user_two.id, business_area.slug)

    grievance_ticket1.refresh_from_db()

    assert grievance_ticket1.assigned_at is not None
    assert grievance_ticket1.assigned_by is None


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
