from faker.generator import random

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.constants import (
    PRIORITY_HIGH,
    PRIORITY_NOT_SET,
    URGENCY_NOT_SET,
    URGENCY_VERY_URGENT,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.bulk_action_service import BulkActionService


class TestGrievanceApproveAutomaticMutation(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
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

    def test_bulk_update_assignee(self) -> None:
        self.assertEqual(self.grievance_ticket1.assigned_to, self.user)
        self.assertEqual(self.grievance_ticket2.assigned_to, self.user)
        BulkActionService().bulk_assign(
            [self.grievance_ticket1.id, self.grievance_ticket2.id], self.user_two.id, self.business_area.slug
        )
        self.grievance_ticket1.refresh_from_db()
        self.grievance_ticket2.refresh_from_db()
        self.assertEqual(self.grievance_ticket1.assigned_to, self.user_two)
        self.assertEqual(self.grievance_ticket2.assigned_to, self.user_two)

    def test_bulk_update_priority(self) -> None:
        self.assertEqual(self.grievance_ticket1.priority, PRIORITY_NOT_SET)
        self.assertEqual(self.grievance_ticket2.priority, PRIORITY_NOT_SET)
        BulkActionService().bulk_set_priority(
            [self.grievance_ticket1.id, self.grievance_ticket2.id], PRIORITY_HIGH, self.business_area.slug
        )
        self.grievance_ticket1.refresh_from_db()
        self.grievance_ticket2.refresh_from_db()
        self.assertEqual(self.grievance_ticket1.priority, PRIORITY_HIGH)
        self.assertEqual(self.grievance_ticket2.priority, PRIORITY_HIGH)

    def test_bulk_update_urgency(self) -> None:
        self.assertEqual(self.grievance_ticket1.urgency, URGENCY_NOT_SET)
        self.assertEqual(self.grievance_ticket2.urgency, URGENCY_NOT_SET)
        BulkActionService().bulk_set_urgency(
            [self.grievance_ticket1.id, self.grievance_ticket2.id], URGENCY_VERY_URGENT, self.business_area.slug
        )
        self.grievance_ticket1.refresh_from_db()
        self.grievance_ticket2.refresh_from_db()
        self.assertEqual(self.grievance_ticket1.urgency, URGENCY_VERY_URGENT)
        self.assertEqual(self.grievance_ticket2.urgency, URGENCY_VERY_URGENT)

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
