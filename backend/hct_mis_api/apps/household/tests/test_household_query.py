from typing import Any, List

from django.conf import settings

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import DocumentFactory, create_household
from hct_mis_api.apps.household.models import DocumentType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.one_time_scripts.migrate_data_to_representations import (
    migrate_data_to_representations_per_business_area,
)

ALL_HOUSEHOLD_QUERY = """
      query AllHouseholds($search: String, $searchType: String, $program: ID) {
        allHouseholds(search: $search, searchType: $searchType, orderBy: "size", program: $program, businessArea: "afghanistan") {
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
ALL_HOUSEHOLD_QUERY_RANGE = """
    query AllHouseholds($program: ID){
      allHouseholds(
        orderBy: "size",
        size: "{\\"min\\": 3, \\"max\\": 9}",
        businessArea: "afghanistan",
        program: $program
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
ALL_HOUSEHOLD_QUERY_MIN = """
    query AllHouseholds($program: ID){
      allHouseholds(orderBy: "size", size: "{\\"min\\": 3}", businessArea: "afghanistan", program: $program) {
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
ALL_HOUSEHOLD_QUERY_MAX = """
    query AllHouseholds($program: ID){
      allHouseholds(orderBy: "size", size: "{\\"max\\": 9}", businessArea: "afghanistan", program: $program) {
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
ALL_HOUSEHOLD_FILTER_PROGRAMS_QUERY = """
    query AllHouseholds {
      allHouseholds(businessArea: "afghanistan") {
        edges {
          node {
            size
            countryOrigin
            address
            programs {
              totalCount
            }
          }
        }
      }
    }
    """
HOUSEHOLD_QUERY = """
    query Household($id: ID!) {
      household(id: $id) {
        size
        countryOrigin
        address
        adminArea {
          pCode
        }
        adminAreaTitle
        admin1 {
          pCode
        }
        admin2 {
          pCode
        }
      }
    }
    """


class TestHouseholdQuery(APITestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        cls.partner = PartnerFactory()
        cls.user = UserFactory.create(partner=cls.partner)
        cls.business_area = create_afghanistan()

        family_sizes_list = (2, 4, 5, 1, 3, 11, 14)
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
        cls.program_draft = ProgramFactory(
            name="Test program DRAFT",
            business_area=cls.business_area,
            status=Program.DRAFT,
        )

        cls.update_user_partner_perm_for_program(cls.user, cls.business_area, cls.program_one)
        cls.update_user_partner_perm_for_program(cls.user, cls.business_area, cls.program_two)
        cls.update_user_partner_perm_for_program(cls.user, cls.business_area, cls.program_draft)

        cls.households = []
        country_origin = geo_models.Country.objects.filter(iso_code2="PL").first()

        for index, family_size in enumerate(family_sizes_list):
            (household, individuals) = create_household(
                {"size": family_size, "address": f"Lorem Ipsum {family_size}", "country_origin": country_origin},
            )
            if index % 2:
                household.programs.add(cls.program_one)
                household.program_id = cls.program_one.pk
                household.save()
            else:
                household.programs.add(cls.program_two)
                household.program_id = cls.program_two.pk
                household.save()
                # added for testing migrate_data_to_representations script
                if family_size == 14:
                    household.programs.add(cls.program_one)

            area_type_level_1 = AreaTypeFactory(
                name="State1",
                area_level=1,
            )
            area_type_level_2 = AreaTypeFactory(
                name="State2",
                area_level=2,
            )
            cls.area1 = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1")
            cls.area2 = AreaFactory(name="City Test2", area_type=area_type_level_2, p_code="area2", parent=cls.area1)
            household.set_admin_areas(cls.area2)

            cls.households.append(household)

        household = cls.households[0]
        household.registration_id = 123
        household.save()
        household.refresh_from_db()
        household.head_of_household.phone_no = "+18663567905"
        household.head_of_household.save()
        household.head_of_household.refresh_from_db()

        DocumentFactory(
            document_number="123-456-789",
            type=DocumentType.objects.get(key="national_id"),
            individual=household.head_of_household,
        )

        cls.partner.permissions = {
            str(cls.business_area.id): {
                "programs": {
                    str(cls.program_one.id): [str(cls.households[0].admin_area.id)],
                    str(cls.program_two.id): [str(cls.households[0].admin_area.id)],
                    str(cls.program_draft.id): [str(cls.households[0].admin_area.id)],
                }
            }
        }
        cls.partner.save()

        # remove after data migration
        BusinessAreaFactory(name="Democratic Republic of Congo")
        BusinessAreaFactory(name="Sudan")
        BusinessAreaFactory(name="Trinidad & Tobago")
        BusinessAreaFactory(name="Slovakia")
        BusinessAreaFactory(name="Sri Lanka")
        migrate_data_to_representations_per_business_area(business_area=cls.business_area)
        super().setUpTestData()

    @parameterized.expand(
        [
            ("all_with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], ALL_HOUSEHOLD_QUERY),
            ("all_without_permission", [], ALL_HOUSEHOLD_QUERY),
            (
                "all_range_with_permission",
                [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
                ALL_HOUSEHOLD_QUERY_RANGE,
            ),
            ("all_range_without_permission", [], ALL_HOUSEHOLD_QUERY_RANGE),
            ("all_min_with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], ALL_HOUSEHOLD_QUERY_MIN),
            ("all_max_with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], ALL_HOUSEHOLD_QUERY_MAX),
        ]
    )
    def test_household_query_all(self, _: Any, permissions: List[Permissions], query_string: str) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=query_string,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"program": self.id_to_base64(self.program_two.id, "ProgramNode")},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_household_query_single(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.households[0].id, "HouseholdNode")},
        )

    def test_household_query_draft(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_draft.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_by_search_household_id_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        household = self.households[0]

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": f"{household.unicef_id}", "searchType": "household_id"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_by_search_individual_id_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        household = self.households[0]

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": f"{household.head_of_household.unicef_id}", "searchType": "individual_id"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_by_search_full_name_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        household = self.households[0]

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": f"{household.head_of_household.full_name}", "searchType": "individual_id"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_by_search_phone_no_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": "+18663567905", "searchType": "phone_no"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_by_national_id_no_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": "123-456-789", "searchType": "national_id"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], "123"),
            ("with_permission_wrong_type_in_search", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], "123/123"),
            ("without_permission", [], "123"),
        ]
    )
    def test_query_households_by_registration_id_filter(
        self, _: Any, permissions: List[Permissions], search: str
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": search, "searchType": "registration_id"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_search_without_search_type(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "search": "123-456-789",
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_search_incorrect_kobo_asset_id(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": "qwerty12345", "searchType": "kobo_asset_id"},
        )
