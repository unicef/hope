from datetime import datetime

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    AdminAreaFactory,
    AdminAreaLevelFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household


class TestGrievanceDashboardQuery(APITestCase):
    TICKETS_BY_TYPE_QUERY = """
    query ticketsByType($businessAreaSlug: String!) {
        ticketsByType(businessAreaSlug: $businessAreaSlug) {
            userGeneratedCount
            systemGeneratedCount
            closedUserGeneratedCount
            closedSystemGeneratedCount
            userGeneratedAvgResolution
            systemGeneratedAvgResolution
        }
    }
    """

    TICKETS_BY_CATEGORY = """
    query ticketsByCategory($businessAreaSlug: String!) {
        ticketsByCategory(businessAreaSlug: $businessAreaSlug) {
            labels
            datasets {
                data
            }
        }
    }
    """

    TICKETS_BY_STATUS = """
    query ticketsByStatus($businessAreaSlug: String!) {
        ticketsByStatus(businessAreaSlug: $businessAreaSlug) {
            labels
            datasets {
                data
            }
        }
    }
    """

    TICKETS_BY_LOCATION = """
    query TicketByLocationAndCategory($businessAreaSlug: String!) {
        ticketsByLocationAndCategory(businessAreaSlug: $businessAreaSlug) {
            location
            count
            categories {
                categoryName
                count
            }
        }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=cls.business_area,
        )
        cls.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="123aa123")

        country = Country.objects.first()
        area_type_new = AreaTypeFactory(
            name="Admin type one",
            area_level=2,
            country=country,
            original_id=area_type.id,
        )
        cls.admin_area_1_new = AreaFactory(
            name="City Test", area_type=area_type_new, p_code="123aa123", original_id=cls.admin_area_1.id
        )

        created_at_dates_to_set = {
            GrievanceTicket.STATUS_NEW: datetime(year=2020, month=3, day=12),
            GrievanceTicket.STATUS_ON_HOLD: datetime(year=2020, month=7, day=12),
            GrievanceTicket.STATUS_IN_PROGRESS: datetime(year=2020, month=8, day=22),
        }

        grievances_to_create = (
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": cls.admin_area_1,
                    "admin2_new": cls.admin_area_1_new,
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
                    "admin2": cls.admin_area_1,
                    "admin2_new": cls.admin_area_1_new,
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
                    "admin2": cls.admin_area_1,
                    "admin2_new": cls.admin_area_1_new,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": cls.admin_area_1,
                    "admin2_new": cls.admin_area_1_new,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_CLOSED,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": cls.admin_area_1,
                    "admin2_new": cls.admin_area_1_new,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    "status": GrievanceTicket.STATUS_CLOSED,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": cls.admin_area_1,
                    "admin2_new": cls.admin_area_1_new,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Just random description",
                    "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    "status": GrievanceTicket.STATUS_CLOSED,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
        )
        GrievanceTicket.objects.bulk_create(grievances_to_create)

        for status, date in created_at_dates_to_set.items():
            gt = GrievanceTicket.objects.get(status=status)
            gt.created_at = date
            gt.updated_at = datetime.now()
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
    def test_grievance_query_by_type(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.TICKETS_BY_TYPE_QUERY,
            context={"user": self.user},
            variables={
                "businessAreaSlug": "afghanistan"
            }
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
    def test_grievance_query_by_category(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.TICKETS_BY_CATEGORY,
            context={"user": self.user},
            variables={
                "businessAreaSlug": "afghanistan"
            }
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
    def test_grievance_query_by_status(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.TICKETS_BY_STATUS,
            context={"user": self.user},
            variables={
                "businessAreaSlug": "afghanistan"
            }
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
    def test_grievance_query_by_location(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.TICKETS_BY_LOCATION,
            context={"user": self.user},
            variables={
                "businessAreaSlug": "afghanistan"
            }
        )

