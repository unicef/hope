from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import cached_business_areas_slug_id_dict
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory

ALL_HOUSEHOLD_QUERY = """
      query AllHouseholds{
        allHouseholds(orderBy: "size", businessArea: "afghanistan") {
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
      }
    }
    """


class TestHouseholdQuery(APITestCase):
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls):
        cached_business_areas_slug_id_dict.cache_clear()
        call_command("loadbusinessareas")
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
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

            cls.households.append(household)

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
    def test_household_query_all(self, _, permissions, query_string):
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
    def test_household_filter_by_programme(self, _, permissions):
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
    def test_household_query_single(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=HOUSEHOLD_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.households[0].id, "HouseholdNode")},
        )
