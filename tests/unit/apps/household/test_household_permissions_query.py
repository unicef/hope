from django.conf import settings

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import (
    create_afghanistan,
    generate_data_collecting_types,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.program import ProgramFactory

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.program.models import Program


class TestHouseholdPermissionsQuery(APITestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    HOUSEHOLD_QUERY = """
    query Household($id: ID!) {
      household(id: $id) {
        size
        admin2 {
          pCode
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.unicef_partner = PartnerFactory(name="UNICEF")
        cls.not_unicef_partner = PartnerFactory(name="NOT_UNICEF")
        cls.user = UserFactory()
        cls.business_area = create_afghanistan()

        generate_data_collecting_types()
        partial = DataCollectingType.objects.get(code="partial_individuals")
        cls.program_one = ProgramFactory(
            name="Test program ONE",
            business_area=cls.business_area,
            status=Program.ACTIVE,
            data_collecting_type=partial,
        )
        cls.program_two = ProgramFactory(
            name="Test program TWO",
            business_area=cls.business_area,
            status=Program.ACTIVE,
            data_collecting_type=partial,
        )

        country_origin = Country.objects.filter(iso_code2="PL").first()

        area_type_level_1 = AreaTypeFactory(
            name="State1",
            area_level=1,
        )
        area_type_level_2 = AreaTypeFactory(
            name="State2",
            area_level=2,
        )
        area1 = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="TEST01")
        cls.area2 = AreaFactory(name="City Test2", area_type=area_type_level_2, p_code="TEST0101", parent=area1)
        cls.area3 = AreaFactory(name="City Test3", area_type=area_type_level_2, p_code="TEST0102", parent=area1)
        cls.household, _ = create_household(
            {"size": 2, "address": "Lorem Ipsum 2", "country_origin": country_origin, "program": cls.program_one},
        )
        cls.household.program = cls.program_one
        cls.household.save()
        cls.household.set_admin_areas(cls.area2)

        permissions = [Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS]
        cls.create_user_role_with_permissions(cls.user, permissions, cls.business_area)

    def test_unicef_partner_has_access_for_program(self) -> None:
        self._test_unicef_partner_has_access(self.id_to_base64(self.program_one.id, "ProgramNode"))

    def test_unicef_partner_has_access_query_all_programs(self) -> None:
        self._test_unicef_partner_has_access("all")

    def _test_unicef_partner_has_access(self, program: str) -> None:
        self.user.partner = self.unicef_partner
        self.user.save()

        self.snapshot_graphql_request(
            request_string=self.HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": program,
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.household.id, "HouseholdNode")},
        )

    def test_not_unicef_partner_with_program_and_with_full_admin_area_has_access_for_program(self) -> None:
        self._test_not_unicef_partner_with_program_and_with_full_admin_area_has_access(
            self.id_to_base64(self.program_one.id, "ProgramNode")
        )

    def test_not_unicef_partner_with_program_and_with_full_admin_area_has_access_query_all_programs(self) -> None:
        self._test_not_unicef_partner_with_program_and_with_full_admin_area_has_access("all")

    def _test_not_unicef_partner_with_program_and_with_full_admin_area_has_access(self, program: str) -> None:
        self.update_partner_access_to_program(self.not_unicef_partner, self.program_one, [self.area2, self.area3])
        self.user.partner = self.not_unicef_partner
        self.user.save()

        self.snapshot_graphql_request(
            request_string=self.HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": program,
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.household.id, "HouseholdNode")},
        )

    def test_not_unicef_partner_with_program_and_with_correct_admin_area_has_access_for_program(self) -> None:
        self._test_not_unicef_partner_with_program_and_with_correct_admin_area_has_access(
            self.id_to_base64(self.program_one.id, "ProgramNode")
        )

    def test_not_unicef_partner_with_program_and_with_correct_admin_area_has_access_query_all_programs(self) -> None:
        self._test_not_unicef_partner_with_program_and_with_correct_admin_area_has_access("all")

    def _test_not_unicef_partner_with_program_and_with_correct_admin_area_has_access(self, program: str) -> None:
        self.update_partner_access_to_program(
            self.not_unicef_partner,
            self.program_one,
            [self.area2],
        )
        self.user.partner = self.not_unicef_partner
        self.user.save()

        self.snapshot_graphql_request(
            request_string=self.HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": program,
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.household.id, "HouseholdNode")},
        )

    def test_not_unicef_partner_with_program_and_with_wrong_admin_area_doesnt_have_access_for_program(self) -> None:
        self._test_not_unicef_partner_with_program_and_with_wrong_admin_area_doesnt_have_access(
            self.id_to_base64(self.program_one.id, "ProgramNode")
        )

    def test_not_unicef_partner_with_program_and_with_wrong_admin_area_doesnt_have_access_query_all_programs(
        self,
    ) -> None:
        self._test_not_unicef_partner_with_program_and_with_wrong_admin_area_doesnt_have_access("all")

    def _test_not_unicef_partner_with_program_and_with_wrong_admin_area_doesnt_have_access(self, program: str) -> None:
        self.update_partner_access_to_program(
            self.not_unicef_partner,
            self.program_one,
            [self.area3],
        )
        self.user.partner = self.not_unicef_partner
        self.user.save()

        self.snapshot_graphql_request(
            request_string=self.HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": program,
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.household.id, "HouseholdNode")},
        )

    def test_not_unicef_partner_without_program_doesnt_have_access_for_program(self) -> None:
        self._test_not_unicef_partner_without_program_doesnt_have_access(
            self.id_to_base64(self.program_one.id, "ProgramNode")
        )

    def test_not_unicef_partner_without_program_doesnt_have_access_query_all_programs(self) -> None:
        self._test_not_unicef_partner_without_program_doesnt_have_access("all")

    def _test_not_unicef_partner_without_program_doesnt_have_access(self, program: str) -> None:
        self.user.partner = self.not_unicef_partner
        self.user.save()

        self.snapshot_graphql_request(
            request_string=self.HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": program,
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.household.id, "HouseholdNode")},
        )
