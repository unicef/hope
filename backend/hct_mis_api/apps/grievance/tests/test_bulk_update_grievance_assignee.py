import random
from unittest.mock import patch

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.grievance.models import GrievanceTicket


class TestUpdateGrievanceTickets(APITestCase):
    BULK_UPDATE_GRIEVANCE_TICKETS_ASSIGNEES_MUTATION = """
    mutation BulkUpdateGrievanceTicketsAssignees(
      $grievanceTicketUnicefIds: [ID], $assignedTo: String, $businessAreaSlug: String!
    ) {
      bulkUpdateGrievanceAssignee(grievanceTicketUnicefIds: $grievanceTicketUnicefIds, assignedTo: $assignedTo, businessAreaSlug: $businessAreaSlug) {
        grievanceTickets {
            assignedTo {
                firstName
            }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory(first_name="user")
        cls.user_two = UserFactory.create(first_name="user_two")
        cls.assignedTo = encode_id_base64(cls.user_two.id, "Grievance")
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

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    @patch("hct_mis_api.apps.grievance.mutations.bulk_update_assigned_to")
    def test_bulk_update_grievance_assignee(self, _, permissions, bulk_update_assigned_to_mock):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        input_data = {
            "businessAreaSlug": self.business_area.slug,
            "grievanceTicketUnicefIds": [
                self.grievance_ticket1.unicef_id,
                self.grievance_ticket2.unicef_id,
                self.grievance_ticket3.unicef_id,
                self.grievance_ticket4.unicef_id,
                "GRV-000030",
            ],
            "assignedTo": self.assignedTo,
        }

        self.snapshot_graphql_request(
            request_string=self.BULK_UPDATE_GRIEVANCE_TICKETS_ASSIGNEES_MUTATION,
            context={"user": self.user},
            variables=input_data,
        )
