from typing import Any, List

from django.core.management import call_command

from extras.test_utils.factories.account import PartnerFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    ReferralTicketWithoutExtrasFactory,
)
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.program import ProgramFactory
from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.program.models import Program


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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()

        call_command("loadcountries")

        cls.partner = PartnerFactory(name="Test1")
        cls.partner_2 = PartnerFactory(name="Test2")
        cls.user = UserFactory.create(partner=cls.partner)
        cls.user2 = UserFactory.create(partner=cls.partner_2)

        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory(business_area=cls.business_area, status=Program.ACTIVE)

        country = Country.objects.first()
        area_type = AreaTypeFactory(
            name="Admin type one",
            area_level=2,
            country=country,
        )
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="123aa123")
        cls.admin_area_2 = AreaFactory(name="City Example", area_type=area_type, p_code="sadasdasfd222")

        # update partner perms
        role = RoleFactory(name="Test Role", permissions=[Permissions.PROGRAMME_CREATE])
        cls.update_partner_access_to_program(cls.partner, cls.program, [cls.admin_area_1, cls.admin_area_2])
        cls.add_partner_role_in_business_area(
            cls.partner,
            cls.business_area,
            [role],
        )
        cls.update_partner_access_to_program(cls.partner_2, cls.program, [cls.admin_area_1, cls.admin_area_2])
        cls.add_partner_role_in_business_area(
            cls.partner_2,
            cls.business_area,
            [role],
        )

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

        cls.ticket_1.programs.add(cls.program)
        cls.ticket_2.programs.add(cls.program)
        cls.ticket_3.programs.add(cls.program)
        cls.ticket_4.programs.add(cls.program)
        cls.ticket_5.programs.add(cls.program)

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
    def test_grievance_query_sort_by_linked_tickets_ascending(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)
        self.snapshot_graphql_request(
            request_string=self.SORT_GRIEVANCE_QUERY_BY_LINKED_TICKETS_ASC,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
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
    def test_grievance_query_sort_by_linked_tickets_descending(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)
        self.snapshot_graphql_request(
            request_string=self.SORT_GRIEVANCE_QUERY_BY_LINKED_TICKETS_DESC,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
        )
