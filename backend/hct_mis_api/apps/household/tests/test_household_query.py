from typing import Any, List

from django.conf import settings

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import DocumentFactory, create_household
from hct_mis_api.apps.household.models import DocumentType
from hct_mis_api.apps.program.fixtures import ProgramFactory

ALL_HOUSEHOLD_QUERY = """
      query AllHouseholds($search: String) {
        allHouseholds(search: $search, orderBy: "size", businessArea: "afghanistan") {
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
    query AllHouseholds{
      allHouseholds(
        orderBy: "size",
        size: "{\\"min\\": 3, \\"max\\": 9}",
        businessArea: "afghanistan"
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
    query AllHouseholds{
      allHouseholds(orderBy: "size", size: "{\\"min\\": 3}", businessArea: "afghanistan") {
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
    query AllHouseholds{
      allHouseholds(orderBy: "size", size: "{\\"max\\": 9}", businessArea: "afghanistan") {
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
    query AllHouseholds($programs:[ID]){
      allHouseholds(programs: $programs, businessArea: "afghanistan") {
        edges {
          node {
            size
            countryOrigin
            address
            programs {
              edges {
                node {
                  name
                }
              }
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
        cls.user = UserFactory.create()
        cls.business_area = create_afghanistan()
        family_sizes_list = (2, 4, 5, 1, 3, 11, 14)
        cls.program_one = ProgramFactory(
            name="Test program ONE",
            business_area=cls.business_area,
        )
        cls.program_two = ProgramFactory(
            name="Test program TWO",
            business_area=cls.business_area,
        )

        cls.households = []
        country_origin = geo_models.Country.objects.filter(iso_code2="PL").first()

        for index, family_size in enumerate(family_sizes_list):
            (household, individuals) = create_household(
                {"size": family_size, "address": "Lorem Ipsum", "country_origin": country_origin},
            )
            if index % 2:
                household.programs.add(cls.program_one)
            else:
                household.programs.add(cls.program_two)

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
        household.refresh_from_db()
        household.head_of_household.phone_no = "+18663567905"
        household.head_of_household.save()

        DocumentFactory(
            document_number="123-456-789",
            type=DocumentType.objects.get(key="national_id"),
            individual=household.head_of_household,
        )

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
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_household_filter_by_programme(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_FILTER_PROGRAMS_QUERY,
            variables={"programs": [self.id_to_base64(self.program_one.id, "ProgramNode")]},
            context={"user": self.user},
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
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.households[0].id, "HouseholdNode")},
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
            context={"user": self.user},
            variables={"search": f"household_id {household.unicef_id}"},
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
            context={"user": self.user},
            variables={"search": f"individual_id {household.head_of_household.unicef_id}"},
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
            context={"user": self.user},
            variables={"search": f"individual_id {household.head_of_household.full_name}"},
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
            context={"user": self.user},
            variables={"search": "phone_no +18663567905"},
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
            context={"user": self.user},
            variables={"search": "national_id 123-456-789"},
        )
