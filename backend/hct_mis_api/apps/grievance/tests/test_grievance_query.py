from datetime import datetime

from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaTypeFactory, AdminAreaFactory
from core.models import BusinessArea
from grievance.models import GrievanceTicket


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

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaTypeFactory(name="Admin type one", admin_level=2, business_area=self.business_area,)
        self.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_type=area_type)
        self.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_type=area_type)

        created_at_dates_to_set = {
            GrievanceTicket.STATUS_OPEN: datetime(year=2020, month=3, day=12),
            GrievanceTicket.STATUS_CLOSED: datetime(year=2020, month=7, day=12),
            GrievanceTicket.STATUS_RESOLVED: datetime(year=2020, month=8, day=22),
        }

        grievances_to_create = (
            GrievanceTicket(
                **{
                    "business_area": self.business_area,
                    "admin": self.admin_area_1.title,
                    "language": "Polish",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_OPEN,
                    "created_by": self.user,
                    "assigned_to": self.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.business_area,
                    "admin": self.admin_area_2.title,
                    "language": "English",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_CLOSED,
                    "created_by": self.user,
                    "assigned_to": self.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.business_area,
                    "admin": self.admin_area_2.title,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_RESOLVED,
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

    def test_grievance_query_all(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_GRIEVANCE_QUERY, context={"user": self.user},
        )

    def test_grievance_query_single(self):
        gt_id = GrievanceTicket.objects.get(status=GrievanceTicket.STATUS_RESOLVED).id
        self.snapshot_graphql_request(
            request_string=self.GRIEVANCE_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(gt_id, "GrievanceTicket")},
        )

    def test_grievance_list_filtered_by_admin2(self):
        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_ADMIN_AREA,
            context={"user": self.user},
            variables={"admin": self.admin_area_1.id},
        )

    def test_grievance_list_filtered_by_created_at(self):
        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"createdAtRange": "{\"min\": \"2020-07-12\", \"max\": \"2020-09-12\"}"},
        )

    def test_grievance_list_filtered_by_status(self):
        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_STATUS,
            context={"user": self.user},
            variables={"status": [str(GrievanceTicket.STATUS_RESOLVED)]},
        )
