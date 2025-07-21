from typing import Any, List

from parameterized import parameterized

from tests.extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.program import ProgramFactory
from hct_mis_api.apps.program.models import Program

ALL_HOUSEHOLD_QUERY = """
  query AllHouseholds($program: ID) {
    allHouseholds(
        orderBy: "size",
        program: $program,
        businessArea: "afghanistan"
        rdiMergeStatus: "MERGED"
    ) {
      edges {
        node {
          size
          countryOrigin
          address
        }
      }
    }
  }
"""


class TestHouseholdAreaQuery(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area_afghanistan = BusinessAreaFactory(slug="afghanistan")
        cls.business_area_ukraine = BusinessAreaFactory(slug="ukraine")

        cls.province = AreaTypeFactory(
            name="Province",
            area_level=1,
        )
        cls.district = AreaTypeFactory(
            name="District",
            area_level=2,
        )
        cls.parish = AreaTypeFactory(
            name="Parish",
            area_level=3,
        )

        cls.ghazni = AreaFactory(name="Ghazni", area_type=cls.province, p_code="area1")
        cls.nawa = AreaFactory(name="Nawa", area_type=cls.district, p_code="area2", parent=cls.ghazni)
        cls.nawur = AreaFactory(name="Nawur", area_type=cls.district, p_code="area3", parent=cls.ghazni)
        cls.abband = AreaFactory(name="Abband", area_type=cls.district, p_code="area4", parent=cls.ghazni)
        cls.zaranj = AreaFactory(name="Zaranj", area_type=cls.parish, p_code="area5", parent=cls.abband)
        cls.lashkaragh = AreaFactory(name="Lashkaragh", area_type=cls.parish, p_code="area6", parent=cls.abband)
        cls.kandahar = AreaFactory(name="Kandahar", area_type=cls.parish, p_code="area7", parent=cls.abband)

        cls.program = ProgramFactory(name="program", business_area=cls.business_area_afghanistan, status=Program.ACTIVE)
        cls.program_2 = ProgramFactory(name="program_2", business_area=cls.business_area_ukraine, status=Program.ACTIVE)

        cls.household_1, _ = create_household({"size": 1, "business_area": cls.business_area_afghanistan})
        cls.household_2, _ = create_household({"size": 2, "business_area": cls.business_area_afghanistan})
        cls.household_3, _ = create_household({"size": 3, "business_area": cls.business_area_afghanistan})
        cls.household_4, _ = create_household({"size": 4, "business_area": cls.business_area_afghanistan})
        cls.household_5, _ = create_household({"size": 5, "business_area": cls.business_area_afghanistan})
        cls.household_6, _ = create_household({"size": 6, "business_area": cls.business_area_afghanistan})

        # Admin 2
        cls.household_1.admin_area = cls.ghazni
        cls.household_1.admin1 = cls.ghazni
        cls.household_1.admin2 = cls.nawa
        cls.household_1.address = "address_1"
        cls.household_1.program = cls.program
        cls.household_1.save()

        # Admin 2
        cls.household_2.admin_area = cls.ghazni
        cls.household_2.admin1 = cls.ghazni
        cls.household_2.admin2 = cls.nawur
        cls.household_2.address = "address_2"
        cls.household_2.program = cls.program
        cls.household_2.save()

        # Admin 3
        cls.household_3.admin_area = cls.ghazni
        cls.household_3.admin1 = cls.ghazni
        cls.household_3.admin2 = cls.abband
        cls.household_3.admin3 = cls.zaranj
        cls.household_3.address = "address_3"
        cls.household_3.program = cls.program
        cls.household_3.save()

        # Admin 3
        cls.household_4.admin_area = cls.ghazni
        cls.household_4.admin1 = cls.ghazni
        cls.household_4.admin2 = cls.abband
        cls.household_4.admin3 = cls.lashkaragh
        cls.household_4.address = "address_4"
        cls.household_4.program = cls.program
        cls.household_4.save()

        # Admin 3
        cls.household_5.admin_area = cls.ghazni
        cls.household_5.admin1 = cls.ghazni
        cls.household_5.admin2 = cls.abband
        cls.household_5.admin3 = cls.kandahar
        cls.household_5.address = "address_5"
        cls.household_5.program = cls.program
        cls.household_5.save()

        # No Admin
        cls.household_6.admin_area = None
        cls.household_6.admin1 = None
        cls.household_6.admin2 = None
        cls.household_6.admin3 = None
        cls.household_6.address = "address_6"
        cls.household_6.program = cls.program
        cls.household_6.save()

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_household_with_no_admin_area_is_filtered(self, _: Any, permissions: List[Permissions]) -> None:
        # No permissions
        partner = PartnerFactory(name="NOT_UNICEF_1")
        user = UserFactory(partner=partner)
        # No access to any admin area
        self.create_user_role_with_permissions(user, permissions, self.business_area_afghanistan, program=self.program)

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area_afghanistan.slug,
                },
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_household_admin_area_3_is_filtered(self, _: Any, permissions: List[Permissions]) -> None:
        # Access to admin3
        partner = PartnerFactory(name="NOT_UNICEF_2")
        user = UserFactory(partner=partner)
        # partner with access to household_5.admin3 in program self.program
        self.create_user_role_with_permissions(
            user, permissions, self.business_area_afghanistan, program=self.program, areas=[self.household_5.admin3]
        )

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area_afghanistan.slug,
                },
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_household_many_admin_area_3_is_filtered(self, _: Any, permissions: List[Permissions]) -> None:
        # Access to many admin3
        partner = PartnerFactory(name="NOT_UNICEF_3")
        user = UserFactory(partner=partner)
        self.create_user_role_with_permissions(
            user,
            permissions,
            self.business_area_afghanistan,
            program=self.program,
            areas=[self.household_4.admin3, self.household_5.admin3],
        )

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area_afghanistan.slug,
                },
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_household_admin_area_2_is_filtered(self, _: Any, permissions: List[Permissions]) -> None:
        # Access to admin2
        partner = PartnerFactory(name="NOT_UNICEF_4")
        user = UserFactory(partner=partner)
        self.create_user_role_with_permissions(
            user, permissions, self.business_area_afghanistan, program=self.program, areas=[self.household_3.admin2]
        )

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area_afghanistan.slug,
                },
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_household_many_admin_area_2_is_filtered(self, _: Any, permissions: List[Permissions]) -> None:
        # Access many admin2
        partner = PartnerFactory(name="NOT_UNICEF_5")
        user = UserFactory(partner=partner)
        self.create_user_role_with_permissions(
            user,
            permissions,
            self.business_area_afghanistan,
            program=self.program,
            areas=[self.household_1.admin2, self.household_2.admin2],
        )

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area_afghanistan.slug,
                },
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_household_admin_area_2_and_admin_area_3_is_filtered(self, _: Any, permissions: List[Permissions]) -> None:
        # Access many admin2 and admin3
        partner = PartnerFactory(name="NOT_UNICEF_6")
        user = UserFactory(partner=partner)
        self.create_user_role_with_permissions(
            user,
            permissions,
            self.business_area_afghanistan,
            program=self.program,
            areas=[self.household_1.admin2, self.household_4.admin3, self.household_5.admin3],
        )

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area_afghanistan.slug,
                },
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_household_admin_area_1_is_filtered(self, _: Any, permissions: List[Permissions]) -> None:
        # Access to admin1
        partner = PartnerFactory(name="NOT_UNICEF_7")
        user = UserFactory(partner=partner)
        self.create_user_role_with_permissions(
            user, permissions, self.business_area_afghanistan, program=self.program, areas=[self.household_1.admin1]
        )

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area_afghanistan.slug,
                },
            },
        )

    @parameterized.expand(
        [
            ("without_user_role_permission",),
        ]
    )
    def test_households_area_filtered_when_partner_is_unicef(self, _: Any) -> None:
        partner = PartnerFactory(name="UNICEF")
        user = UserFactory(partner=partner)
        self.create_user_role_with_permissions(
            user, [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], self.business_area_afghanistan
        )
        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area_afghanistan.slug,
                },
            },
        )
