from datetime import datetime
from typing import Any, List

from django.core.management import call_command

import pytz
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.models import GrievanceTicket


class TestGrievanceDashboardQuery(APITestCase):
    TICKETS_BY_TYPE_QUERY = """
    query ticketsByType($businessAreaSlug: String!) {
        ticketsByType(businessAreaSlug: $businessAreaSlug) {
            userGeneratedCount
            systemGeneratedCount
            closedUserGeneratedCount
            closedSystemGeneratedCount
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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadcountries")
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        country = Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            area_level=2,
            country=country,
        )
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="123aa123")

        created_at_dates_to_set = {
            GrievanceTicket.STATUS_NEW: datetime(year=2020, month=3, day=12, tzinfo=pytz.UTC),
            GrievanceTicket.STATUS_ON_HOLD: datetime(year=2020, month=7, day=12, tzinfo=pytz.UTC),
            GrievanceTicket.STATUS_IN_PROGRESS: datetime(year=2020, month=8, day=22, tzinfo=pytz.UTC),
        }

        grievances_to_create = (
            GrievanceTicket(
                **{
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_NEW,
                }
            ),
            GrievanceTicket(
                **{
                    "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_ON_HOLD,
                }
            ),
            GrievanceTicket(
                **{
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                }
            ),
            GrievanceTicket(
                **{
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_CLOSED,
                }
            ),
            GrievanceTicket(
                **{
                    "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    "status": GrievanceTicket.STATUS_CLOSED,
                }
            ),
            GrievanceTicket(
                **{
                    "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    "status": GrievanceTicket.STATUS_CLOSED,
                }
            ),
        )

        for grievance_ticket in grievances_to_create:
            grievance_ticket.created_at = cls.user
            grievance_ticket.assigned_to = cls.user
            grievance_ticket.business_area = cls.business_area
            grievance_ticket.admin2 = cls.admin_area_1
            grievance_ticket.consent = True
            grievance_ticket.language = "Polish, English"
            grievance_ticket.description = "Just random description"

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
    def test_grievance_query_by_type(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.TICKETS_BY_TYPE_QUERY,
            context={"user": self.user},
            variables={"businessAreaSlug": "afghanistan"},
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
    def test_grievance_query_by_category(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.TICKETS_BY_CATEGORY,
            context={"user": self.user},
            variables={"businessAreaSlug": "afghanistan"},
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
    def test_grievance_query_by_status(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.TICKETS_BY_STATUS,
            context={"user": self.user},
            variables={"businessAreaSlug": "afghanistan"},
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
    def test_grievance_query_by_location(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.TICKETS_BY_LOCATION,
            context={"user": self.user},
            variables={"businessAreaSlug": "afghanistan"},
        )
