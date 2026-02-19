from typing import Any
from unittest.mock import patch

from flaky import flaky
import pytest

from extras.test_utils.factories import BusinessAreaFactory, GrievanceTicketFactory, UserFactory
from hope.apps.grievance.constants import (
    PRIORITY_HIGH,
    PRIORITY_NOT_SET,
    URGENCY_NOT_SET,
    URGENCY_VERY_URGENT,
)
from hope.apps.grievance.documents import GrievanceTicketDocument
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.bulk_action_service import BulkActionService
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.models import BusinessArea, User

pytestmark = [
    pytest.mark.usefixtures("django_elasticsearch_setup"),
    pytest.mark.elasticsearch,
    pytest.mark.skip("Too flaky, hard to pass, need to fix"),
]


@pytest.fixture(autouse=True)
def enable_elasticsearch_dsl_autosync(settings: Any) -> None:
    settings.ELASTICSEARCH_DSL_AUTOSYNC = True


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
    rebuild_search_index()
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


@flaky(max_runs=3, min_passes=1)
def test_bulk_update_assignee(grievance_context: dict[str, Any]) -> None:
    from elasticsearch.helpers import bulk as original_bulk

    user = grievance_context["users"]["user"]
    user_two = grievance_context["users"]["user_two"]
    business_area = grievance_context["business_area"]
    grievance_ticket1, grievance_ticket2, _, _ = grievance_context["grievance_tickets"]
    with patch("elasticsearch.helpers.bulk") as mock_bulk:
        mock_bulk.side_effect = lambda *args, **kwargs: original_bulk(*args, **kwargs, refresh="wait_for")
        assert grievance_ticket1.assigned_to == user
        assert grievance_ticket2.assigned_to == user
        all_documents = GrievanceTicketDocument.search().query("match_all").execute()
        grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}
        assert grievance_tickets_documents_dict[str(grievance_ticket1.id)].assigned_to.id == str(user.id)
        assert grievance_tickets_documents_dict[str(grievance_ticket2.id)].assigned_to.id == str(user.id)
        BulkActionService().bulk_assign(
            [grievance_ticket1.id, grievance_ticket2.id],
            user_two.id,
            business_area.slug,
        )
        assert mock_bulk.call_count == 2

        grievance_ticket1.refresh_from_db()
        grievance_ticket2.refresh_from_db()

        assert grievance_ticket1.assigned_to == user_two
        assert grievance_ticket2.assigned_to == user_two
        assert grievance_ticket1.status == GrievanceTicket.STATUS_FOR_APPROVAL
        assert grievance_ticket2.status == GrievanceTicket.STATUS_ASSIGNED

        all_documents = GrievanceTicketDocument.search().query("match_all").execute()
        grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}

        assert grievance_tickets_documents_dict[str(grievance_ticket1.id)].assigned_to.id == str(user_two.id)
        assert grievance_tickets_documents_dict[str(grievance_ticket1.id)].status == GrievanceTicket.STATUS_FOR_APPROVAL
        assert grievance_tickets_documents_dict[str(grievance_ticket2.id)].assigned_to.id == str(user_two.id)
        assert grievance_tickets_documents_dict[str(grievance_ticket2.id)].status == GrievanceTicket.STATUS_ASSIGNED


@flaky(max_runs=5, min_passes=1)
def test_bulk_update_priority(grievance_context: dict[str, Any]) -> None:
    from elasticsearch.helpers import bulk as original_bulk

    business_area = grievance_context["business_area"]
    grievance_ticket1, grievance_ticket2, _, _ = grievance_context["grievance_tickets"]
    with patch("elasticsearch.helpers.bulk") as mock_bulk:
        mock_bulk.side_effect = lambda *args, **kwargs: original_bulk(*args, **kwargs, refresh="wait_for")
        assert grievance_ticket1.priority == PRIORITY_NOT_SET
        assert grievance_ticket2.priority == PRIORITY_NOT_SET
        all_documents = GrievanceTicketDocument.search().query("match_all").execute()
        grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}
        assert grievance_tickets_documents_dict[str(grievance_ticket1.id)].priority == PRIORITY_NOT_SET
        assert grievance_tickets_documents_dict[str(grievance_ticket2.id)].priority == PRIORITY_NOT_SET
        BulkActionService().bulk_set_priority(
            [grievance_ticket1.id, grievance_ticket2.id],
            PRIORITY_HIGH,
            business_area.slug,
        )
        grievance_ticket1.refresh_from_db()
        grievance_ticket2.refresh_from_db()
        assert grievance_ticket1.priority == PRIORITY_HIGH
        assert grievance_ticket2.priority == PRIORITY_HIGH
        all_documents = GrievanceTicketDocument.search().query("match_all").execute()
        grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}
        assert grievance_tickets_documents_dict[str(grievance_ticket1.id)].priority == PRIORITY_HIGH
        assert grievance_tickets_documents_dict[str(grievance_ticket2.id)].priority == PRIORITY_HIGH


@flaky(max_runs=5, min_passes=1)
def test_bulk_update_urgency(grievance_context: dict[str, Any]) -> None:
    from elasticsearch.helpers import bulk as original_bulk

    business_area = grievance_context["business_area"]
    grievance_ticket1, grievance_ticket2, _, _ = grievance_context["grievance_tickets"]
    with patch("elasticsearch.helpers.bulk") as mock_bulk:
        mock_bulk.side_effect = lambda *args, **kwargs: original_bulk(*args, **kwargs, refresh="wait_for")
        assert grievance_ticket1.urgency == URGENCY_NOT_SET
        assert grievance_ticket2.urgency == URGENCY_NOT_SET
        all_documents = GrievanceTicketDocument.search().query("match_all").execute()
        grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}
        assert grievance_tickets_documents_dict[str(grievance_ticket1.id)].urgency == URGENCY_NOT_SET
        assert grievance_tickets_documents_dict[str(grievance_ticket2.id)].urgency == URGENCY_NOT_SET
        BulkActionService().bulk_set_urgency(
            [grievance_ticket1.id, grievance_ticket2.id],
            URGENCY_VERY_URGENT,
            business_area.slug,
        )
        grievance_ticket1.refresh_from_db()
        grievance_ticket2.refresh_from_db()
        assert grievance_ticket1.urgency == URGENCY_VERY_URGENT
        assert grievance_ticket2.urgency == URGENCY_VERY_URGENT
        all_documents = GrievanceTicketDocument.search().query("match_all").execute()
        grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}
        assert grievance_tickets_documents_dict[str(grievance_ticket1.id)].urgency == URGENCY_VERY_URGENT
        assert grievance_tickets_documents_dict[str(grievance_ticket2.id)].urgency == URGENCY_VERY_URGENT


@flaky(max_runs=3, min_passes=1)
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
