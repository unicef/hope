from datetime import datetime

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import AdminAreaFactory, AdminAreaLevelFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import GrievanceTicket


class TestGrievanceQuery(APITestCase):
    ALL_GRIEVANCE_QUERY = """
    query AllGrievanceTickets {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at") {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_ADMIN_AREA = """
    query AllGrievanceTickets($admin: [ID]) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", admin: $admin) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_CREATED_AT = """
    query AllGrievanceTickets($createdAtRange: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", createdAtRange: $createdAtRange) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_STATUS = """
    query AllGrievanceTickets($status: [String]) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", status: $status) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    GRIEVANCE_QUERY = """
    query GrievanceTicket($id: ID!) {
      grievanceTicket(id: $id) {
        status
        category
        admin
        language
        description
        consent
        createdAt
      }
    }
    """

    FILTER_BY_CATEGORY = """
    query AllGrievanceTickets($category: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", category: $category) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_ASSIGNED_TO = """
    query AllGrievanceTickets($assignedTo: ID) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", assignedTo: $assignedTo) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.user2 = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=self.business_area,
        )
        self.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="123aa123")
        self.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_level=area_type, p_code="sadasdasfd222")

        created_at_dates_to_set = {
            GrievanceTicket.STATUS_NEW: datetime(year=2020, month=3, day=12),
            GrievanceTicket.STATUS_ON_HOLD: datetime(year=2020, month=7, day=12),
            GrievanceTicket.STATUS_IN_PROGRESS: datetime(year=2020, month=8, day=22),
        }

        grievances_to_create = (
            GrievanceTicket(
                **{
                    "business_area": self.business_area,
                    "admin2": self.admin_area_1,
                    "language": "Polish",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_NEW,
                    "created_by": self.user,
                    "assigned_to": self.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.business_area,
                    "admin2": self.admin_area_2,
                    "language": "English",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_ON_HOLD,
                    "created_by": self.user,
                    "assigned_to": self.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.business_area,
                    "admin2": self.admin_area_2,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": self.user,
                    "assigned_to": self.user,
                }
            ),
        )
        GrievanceTicket.objects.bulk_create(grievances_to_create)

        for status, date in created_at_dates_to_set.items():
            gt = GrievanceTicket.objects.get(status=status)
            gt.created_at = date
            gt.save()

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            ),
            ("without_permission", []),
        ]
    )
    def test_grievance_query_all(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.ALL_GRIEVANCE_QUERY,
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR]),
            ("without_permission", []),
        ]
    )
    def test_grievance_query_single(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        gt_id = GrievanceTicket.objects.get(status=GrievanceTicket.STATUS_IN_PROGRESS).id
        self.snapshot_graphql_request(
            request_string=self.GRIEVANCE_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(gt_id, "GrievanceTicketNode")},
        )

    def test_grievance_list_filtered_by_admin2(self):
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_ADMIN_AREA,
            context={"user": self.user},
            variables={"admin": self.admin_area_1.id},
        )

    def test_grievance_list_filtered_by_created_at(self):
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"createdAtRange": '{"min": "2020-07-12", "max": "2020-09-12"}'},
        )

    def test_grievance_list_filtered_by_status(self):
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_STATUS,
            context={"user": self.user},
            variables={"status": [str(GrievanceTicket.STATUS_IN_PROGRESS)]},
        )

    @parameterized.expand(
        [
            (
                "category_positive_feedback",
                GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            ),
            (
                "category_negative_feedback",
                GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            ),
        ]
    )
    def test_grievance_list_filtered_by_category(self, _, category):
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CATEGORY,
            context={"user": self.user},
            variables={"category": str(category)},
        )

    def test_grievance_list_filtered_by_assigned_to_correct_user(self):
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_ASSIGNED_TO,
            context={"user": self.user},
            variables={"assignedTo": self.id_to_base64(self.user.id, "UserNode")},
        )

    def test_grievance_list_filtered_by_assigned_to_incorrect_user(self):
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_ASSIGNED_TO,
            context={"user": self.user},
            variables={"assignedTo": self.id_to_base64(self.user2.id, "UserNode")},
        )
