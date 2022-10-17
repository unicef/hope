from unittest.mock import patch

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    ReferralTicketWithoutExtrasFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household


@patch("hct_mis_api.apps.core.es_filters.ElasticSearchFilterSet.USE_ALL_FIELDS_AS_POSTGRES_DB", True)
class TestGrievanceQuery(APITestCase):
    SORT_GRIEVANCE_QUERY_BY_LINKED_TICKETS_ASC = """
    query AllGrievanceTickets {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "linked_tickets") {
        edges {
          node {
            description
          }
        }
      }
    }
    """

    SORT_GRIEVANCE_QUERY_BY_LINKED_TICKETS_DESC = """
    query AllGrievanceTickets {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "-linked_tickets") {
        edges {
          node {
            description
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()

        call_command("loadcountries")
        cls.user = UserFactory.create()
        cls.user2 = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = Country.objects.first()
        area_type = AreaTypeFactory(
            name="Admin type one",
            area_level=2,
            country=country,
        )
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="123aa123")
        cls.admin_area_2 = AreaFactory(name="City Example", area_type=area_type, p_code="sadasdasfd222")

        household_1, _ = create_household({"size": 1})
        household_2, _ = create_household({"size": 1})

        household_1.unicef_id = "HH-20-0000.0001"
        household_1.save()

        household_2.unicef_id = "HH-20-0000.0002"
        household_2.save()

        cls.ticket_1 = GrievanceTicketFactory(category=GrievanceTicket.CATEGORY_REFERRAL, description="5")
        ReferralTicketWithoutExtrasFactory(ticket=cls.ticket_1, household=household_1)

        cls.ticket_2 = GrievanceTicketFactory(category=GrievanceTicket.CATEGORY_REFERRAL, description="3")
        ReferralTicketWithoutExtrasFactory(ticket=cls.ticket_2, household=household_1)

        cls.ticket_3 = GrievanceTicketFactory(category=GrievanceTicket.CATEGORY_REFERRAL, description="4")
        ReferralTicketWithoutExtrasFactory(ticket=cls.ticket_3, household=household_1)

        cls.ticket_4 = GrievanceTicketFactory(category=GrievanceTicket.CATEGORY_REFERRAL, description="1")
        ReferralTicketWithoutExtrasFactory(ticket=cls.ticket_4, household=household_2)

        cls.ticket_5 = GrievanceTicketFactory(category=GrievanceTicket.CATEGORY_REFERRAL, description="2")
        ReferralTicketWithoutExtrasFactory(ticket=cls.ticket_5)

        cls.ticket_1.linked_tickets.add(cls.ticket_5)

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            ),
            ("without_permission", []),
        ]
    )
    def test_grievance_query_sort_by_linked_tickets_ascending(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.SORT_GRIEVANCE_QUERY_BY_LINKED_TICKETS_ASC,
            context={"user": self.user},
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
    def test_grievance_query_sort_by_linked_tickets_descending(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.SORT_GRIEVANCE_QUERY_BY_LINKED_TICKETS_DESC, context={"user": self.user}
        )
