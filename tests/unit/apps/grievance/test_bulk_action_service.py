from unittest.mock import patch

from django.test import TestCase, override_settings

import pytest
from faker.generator import random
from flaky import flaky

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.constants import (
    PRIORITY_HIGH,
    PRIORITY_NOT_SET,
    URGENCY_NOT_SET,
    URGENCY_VERY_URGENT,
)
from hct_mis_api.apps.grievance.documents import GrievanceTicketDocument
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.bulk_action_service import BulkActionService
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@override_settings(ELASTICSEARCH_DSL_AUTOSYNC=True)
@pytest.mark.skip("Too flaky, hard to pass, need to fix")
class TestGrievanceApproveAutomaticMutation(TestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.user = UserFactory(first_name="user")
        cls.user_two = UserFactory.create(first_name="user_two")
        # cls.assignedTo = encode_id_base64(cls.user_two.id, "Grievance")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.grievance_ticket1 = GrievanceTicket.objects.create(
            description="Test 1",
            assigned_to=cls.user,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            language="PL",
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            created_by=cls.user,
            business_area=cls.business_area,
            issue_type=random.choice(
                list(GrievanceTicket.ISSUE_TYPES_CHOICES[GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT].keys())
            ),
        )
        cls.grievance_ticket2 = GrievanceTicket.objects.create(
            description="Test 2",
            assigned_to=cls.user,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            language="PL",
            status=GrievanceTicket.STATUS_NEW,
            created_by=cls.user,
            business_area=cls.business_area,
            issue_type=random.choice(
                list(GrievanceTicket.ISSUE_TYPES_CHOICES[GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT].keys())
            ),
        )
        cls.grievance_ticket3 = GrievanceTicket.objects.create(
            description="Test 3",
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            language="PL",
            status=GrievanceTicket.STATUS_NEW,
            created_by=cls.user,
            business_area=cls.business_area,
            issue_type=None,
        )
        cls.grievance_ticket4 = GrievanceTicket.objects.create(
            description="Test 4",
            assigned_to=cls.user_two,
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            language="PL",
            status=GrievanceTicket.STATUS_NEW,
            created_by=cls.user,
            business_area=cls.business_area,
            issue_type=None,
        )
        rebuild_search_index()

    @flaky(max_runs=3, min_passes=1)
    def test_bulk_update_assignee(self) -> None:
        from elasticsearch.helpers import bulk as original_bulk

        with patch("elasticsearch.helpers.bulk") as mock_bulk:
            mock_bulk.side_effect = lambda *args, **kwargs: original_bulk(*args, **kwargs, refresh="wait_for")
            self.assertEqual(self.grievance_ticket1.assigned_to, self.user)
            self.assertEqual(self.grievance_ticket2.assigned_to, self.user)
            all_documents = GrievanceTicketDocument.search().query("match_all").execute()
            grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}
            self.assertEqual(
                grievance_tickets_documents_dict[str(self.grievance_ticket1.id)].assigned_to.id, str(self.user.id)
            )
            self.assertEqual(
                grievance_tickets_documents_dict[str(self.grievance_ticket2.id)].assigned_to.id, str(self.user.id)
            )
            BulkActionService().bulk_assign(
                [self.grievance_ticket1.id, self.grievance_ticket2.id], self.user_two.id, self.business_area.slug
            )
            self.assertEqual(mock_bulk.call_count, 2)

            self.grievance_ticket1.refresh_from_db()
            self.grievance_ticket2.refresh_from_db()

            self.assertEqual(self.grievance_ticket1.assigned_to, self.user_two)
            self.assertEqual(self.grievance_ticket2.assigned_to, self.user_two)

            self.assertEqual(self.grievance_ticket1.status, GrievanceTicket.STATUS_FOR_APPROVAL)
            self.assertEqual(self.grievance_ticket2.status, GrievanceTicket.STATUS_ASSIGNED)

            all_documents = GrievanceTicketDocument.search().query("match_all").execute()
            grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}

            self.assertEqual(
                grievance_tickets_documents_dict[str(self.grievance_ticket1.id)].assigned_to.id, str(self.user_two.id)
            )
            self.assertEqual(
                grievance_tickets_documents_dict[str(self.grievance_ticket1.id)].status,
                GrievanceTicket.STATUS_FOR_APPROVAL,
            )

            self.assertEqual(
                grievance_tickets_documents_dict[str(self.grievance_ticket2.id)].assigned_to.id, str(self.user_two.id)
            )
            self.assertEqual(
                grievance_tickets_documents_dict[str(self.grievance_ticket2.id)].status, GrievanceTicket.STATUS_ASSIGNED
            )

    @flaky(max_runs=5, min_passes=1)
    def test_bulk_update_priority(self) -> None:
        from elasticsearch.helpers import bulk as original_bulk

        with patch("elasticsearch.helpers.bulk") as mock_bulk:
            mock_bulk.side_effect = lambda *args, **kwargs: original_bulk(*args, **kwargs, refresh="wait_for")
            self.assertEqual(self.grievance_ticket1.priority, PRIORITY_NOT_SET)
            self.assertEqual(self.grievance_ticket2.priority, PRIORITY_NOT_SET)
            all_documents = GrievanceTicketDocument.search().query("match_all").execute()
            grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}
            self.assertEqual(
                grievance_tickets_documents_dict[str(self.grievance_ticket1.id)].priority, PRIORITY_NOT_SET
            )
            self.assertEqual(
                grievance_tickets_documents_dict[str(self.grievance_ticket2.id)].priority, PRIORITY_NOT_SET
            )
            BulkActionService().bulk_set_priority(
                [self.grievance_ticket1.id, self.grievance_ticket2.id], PRIORITY_HIGH, self.business_area.slug
            )
            self.grievance_ticket1.refresh_from_db()
            self.grievance_ticket2.refresh_from_db()
            self.assertEqual(self.grievance_ticket1.priority, PRIORITY_HIGH)
            self.assertEqual(self.grievance_ticket2.priority, PRIORITY_HIGH)
            all_documents = GrievanceTicketDocument.search().query("match_all").execute()
            grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}
            self.assertEqual(grievance_tickets_documents_dict[str(self.grievance_ticket1.id)].priority, PRIORITY_HIGH)
            self.assertEqual(grievance_tickets_documents_dict[str(self.grievance_ticket2.id)].priority, PRIORITY_HIGH)

    @flaky(max_runs=5, min_passes=1)
    def test_bulk_update_urgency(self) -> None:
        from elasticsearch.helpers import bulk as original_bulk

        with patch("elasticsearch.helpers.bulk") as mock_bulk:
            mock_bulk.side_effect = lambda *args, **kwargs: original_bulk(*args, **kwargs, refresh="wait_for")
            self.assertEqual(self.grievance_ticket1.urgency, URGENCY_NOT_SET)
            self.assertEqual(self.grievance_ticket2.urgency, URGENCY_NOT_SET)
            all_documents = GrievanceTicketDocument.search().query("match_all").execute()
            grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}
            self.assertEqual(grievance_tickets_documents_dict[str(self.grievance_ticket1.id)].urgency, URGENCY_NOT_SET)
            self.assertEqual(grievance_tickets_documents_dict[str(self.grievance_ticket2.id)].urgency, URGENCY_NOT_SET)
            BulkActionService().bulk_set_urgency(
                [self.grievance_ticket1.id, self.grievance_ticket2.id], URGENCY_VERY_URGENT, self.business_area.slug
            )
            self.grievance_ticket1.refresh_from_db()
            self.grievance_ticket2.refresh_from_db()
            self.assertEqual(self.grievance_ticket1.urgency, URGENCY_VERY_URGENT)
            self.assertEqual(self.grievance_ticket2.urgency, URGENCY_VERY_URGENT)
            all_documents = GrievanceTicketDocument.search().query("match_all").execute()
            grievance_tickets_documents_dict = {document.meta.id: document for document in all_documents}
            self.assertEqual(
                grievance_tickets_documents_dict[str(self.grievance_ticket1.id)].urgency, URGENCY_VERY_URGENT
            )
            self.assertEqual(
                grievance_tickets_documents_dict[str(self.grievance_ticket2.id)].urgency, URGENCY_VERY_URGENT
            )

    @flaky(max_runs=3, min_passes=1)
    def test_bulk_add_note(self) -> None:
        self.assertEqual(self.grievance_ticket1.ticket_notes.count(), 0)
        self.assertEqual(self.grievance_ticket2.ticket_notes.count(), 0)
        BulkActionService().bulk_add_note(
            self.user, [self.grievance_ticket1.id, self.grievance_ticket2.id], "Test note", self.business_area.slug
        )
        self.grievance_ticket1.refresh_from_db()
        self.grievance_ticket2.refresh_from_db()
        self.assertEqual(self.grievance_ticket1.ticket_notes.count(), 1)
        self.assertEqual(self.grievance_ticket2.ticket_notes.count(), 1)
        self.assertEqual(self.grievance_ticket1.ticket_notes.first().description, "Test note")
