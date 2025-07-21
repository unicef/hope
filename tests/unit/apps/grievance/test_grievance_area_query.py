from typing import Any, List
from unittest import skip

from django.core.management import call_command

from parameterized import parameterized

from tests.extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.grievance import GrievanceTicketFactory
from tests.extras.test_utils.factories.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

ALL_GRIEVANCE_QUERY = """
    query AllGrievanceTickets {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at") {
        edges {
          node {
            description
          }
        }
      }
    }
    """


class TestGrievanceAreaQuery(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        call_command("loadcountries")

        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.ukraine_business_area = BusinessAreaFactory(slug="ukraine")
        cls.program = ProgramFactory(business_area=cls.business_area, status=Program.ACTIVE)

        cls.area_type_level_1 = AreaTypeFactory(name="Province", area_level=1)
        cls.area_type_level_2 = AreaTypeFactory(name="District", area_level=2, parent=cls.area_type_level_1)

        cls.ghazni = AreaFactory(name="Ghazni", area_type=cls.area_type_level_1, p_code="area1")
        cls.doshi = AreaFactory(name="Doshi", area_type=cls.area_type_level_2, p_code="area2", parent=cls.ghazni)
        cls.burka = AreaFactory(name="Burka", area_type=cls.area_type_level_2, p_code="area3", parent=cls.ghazni)
        cls.quadis = AreaFactory(name="Quadis", area_type=cls.area_type_level_2, p_code="area3", parent=cls.ghazni)

        cls.grievance_1 = GrievanceTicketFactory(admin2=cls.doshi, description="doshi", business_area=cls.business_area)
        cls.grievance_2 = GrievanceTicketFactory(admin2=cls.burka, description="burka", business_area=cls.business_area)
        cls.grievance_3 = GrievanceTicketFactory(
            admin2=cls.quadis, description="quadis", business_area=cls.business_area
        )
        cls.grievance_4 = GrievanceTicketFactory(admin2=None, description="no_admin", business_area=cls.business_area)

        cls.grievance_1.programs.add(cls.program)
        cls.grievance_2.programs.add(cls.program)
        cls.grievance_3.programs.add(cls.program)
        cls.grievance_4.programs.add(cls.program)

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            ),
            ("without_permission", []),
        ]
    )
    @skip(reason="Check after merge")
    def test_admin2_null_is_filtered(self, _: Any, permissions: List[Permissions]) -> None:
        partner = PartnerFactory(name="NOT_UNICEF_1")
        user = UserFactory(partner=partner)
        self.create_user_role_with_permissions(user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_GRIEVANCE_QUERY,
            context={
                "user": user,
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
                [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            ),
            ("without_permission", []),
        ]
    )
    def test_one_admin2_is_filtered(self, _: Any, permissions: List[Permissions]) -> None:
        partner = PartnerFactory(name="NOT_UNICEF_2")
        self.update_partner_access_to_program(partner, self.program, [self.doshi])
        user = UserFactory(partner=partner)
        self.create_user_role_with_permissions(user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_GRIEVANCE_QUERY,
            context={
                "user": user,
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
                [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            ),
            ("without_permission", []),
        ]
    )
    @skip("Fail on pipeline")
    def test_many_admin2_is_filtered(self, _: Any, permissions: List[Permissions]) -> None:
        partner = PartnerFactory(name="NOT_UNICEF_3")
        self.update_partner_access_to_program(partner, self.program, [self.doshi, self.burka, self.quadis])
        user = UserFactory(partner=partner)
        self.create_user_role_with_permissions(user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_GRIEVANCE_QUERY,
            context={
                "user": user,
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
                [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            ),
            ("without_permission", []),
        ]
    )
    @skip("Fail on pipeline")
    def test_grievance_ticket_are_filtered_when_partner_is_unicef(self, _: Any, permissions: List[Permissions]) -> None:
        partner = PartnerFactory(name="UNICEF_4")
        user = UserFactory(partner=partner)
        self.create_user_role_with_permissions(user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_GRIEVANCE_QUERY,
            context={
                "user": user,
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
                [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            ),
            ("without_permission", []),
        ]
    )
    @skip("Fail on pipeline")
    def test_admin2_is_filtered_when_partner_has_business_area_access(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        partner = PartnerFactory(name="NOT_UNICEF_5")
        self.update_partner_access_to_program(partner, self.program, [self.doshi, self.burka, self.quadis])
        user = UserFactory(partner=partner)
        self.create_user_role_with_permissions(user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_GRIEVANCE_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
        )
