from datetime import datetime
from django.utils import timezone

from django.core.management import call_command

from parameterized import parameterized
from django.conf import settings

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.fixtures import create_household


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

    FILTER_BY_SCORE = """
    query AllGrievanceTickets($scoreMin: String, $scoreMax: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", scoreMax: $scoreMax, scoreMin: $scoreMin) {
        edges {
          node {
            needsAdjudicationTicketDetails {
              scoreMin
              scoreMax
            }
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

    @classmethod
    def setUpTestData(cls):
        settings.ELASTICSEARCH_GRIEVANCE_TURN_ON = False

        create_afghanistan()
        call_command("loadcountries")
        cls.user = UserFactory.create()
        cls.user2 = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = Country.objects.first()
        area_type_new = AreaTypeFactory(
            name="Admin type one",
            area_level=2,
            country=country,
        )
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type_new, p_code="123aa123")
        cls.admin_area_2 = AreaFactory(name="City Example", area_type=area_type_new, p_code="sadasdasfd222")

        _, individuals = create_household({"size": 2})
        cls.individual_1 = individuals[0]
        cls.individual_2 = individuals[1]

        created_at_dates_to_set = {
            GrievanceTicket.STATUS_NEW: timezone.make_aware(datetime(year=2020, month=3, day=12)),
            GrievanceTicket.STATUS_ON_HOLD: timezone.make_aware(datetime(year=2020, month=7, day=12)),
            GrievanceTicket.STATUS_IN_PROGRESS: timezone.make_aware(datetime(year=2020, month=8, day=22)),
        }

        grievances_to_create = (
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": cls.admin_area_1,
                    "language": "Polish",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_NEW,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": cls.admin_area_2,
                    "language": "English",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_ON_HOLD,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": cls.admin_area_2,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
        )
        GrievanceTicket.objects.bulk_create(grievances_to_create)

        for status, date in created_at_dates_to_set.items():
            gt = GrievanceTicket.objects.get(status=status)
            gt.created_at = date
            gt.save()

        TicketNeedsAdjudicationDetails.objects.create(
            ticket=GrievanceTicket.objects.first(),
            golden_records_individual=cls.individual_1,
            possible_duplicate=cls.individual_2,
            score_min=100,
            score_max=150,
        )

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

    def test_grievance_list_filtered_by_score(self):
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_SCORE,
            context={"user": self.user},
            variables={"scoreMin": 100, "scoreMax": 200},
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_SCORE,
            context={"user": self.user},
            variables={"scoreMin": 900, "scoreMax": 999},
        )
