from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea
from household.fixtures import HouseholdFactory
from program.fixtures import ProgramFactory


class TestHouseholdQuery(APITestCase):
    ALL_HOUSEHOLD_QUERY = """
    query AllHouseholds{
      allHouseholds(orderBy: "size") {
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
        size: "{\\"min\\": 3, \\"max\\": 9}"
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
      allHouseholds(orderBy: "size", size: "{\\"min\\": 3}") {
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
      allHouseholds(orderBy: "size", size: "{\\"max\\": 9}") {
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
      allHouseholds(programs: $programs) {
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

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        family_sizes_list = (2, 4, 5, 1, 3, 11, 14)
        self.program_one = ProgramFactory(
            name="Test program ONE", business_area=BusinessArea.objects.first(),
        )
        self.program_two = ProgramFactory(
            name="Test program TWO", business_area=BusinessArea.objects.first(),
        )

        self.households = []
        for index, family_size in enumerate(family_sizes_list):
            household = HouseholdFactory(
                size=family_size,
                address="Lorem Ipsum",
                country_origin="PL",
                household_ca_id="123-123-123",
            )
            if index % 2:
                household.programs.add(self.program_one)
            else:
                household.programs.add(self.program_two)

            self.households.append(household)

    def test_household_query_all(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_HOUSEHOLD_QUERY,
            context={"user": self.user},
        )

    def test_household_query_all_range(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_HOUSEHOLD_QUERY_RANGE,
            context={"user": self.user},
        )

    def test_household_query_all_min(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_HOUSEHOLD_QUERY_MIN,
            context={"user": self.user},
        )

    def test_household_query_all_max(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_HOUSEHOLD_QUERY_MAX,
            context={"user": self.user},
        )

    def test_household_filter_by_programme(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_HOUSEHOLD_FILTER_PROGRAMS_QUERY,
            variables={
                "programs": [
                    self.id_to_base64(self.program_one.id, "Program")
                ]
            },
            context={"user": self.user},
        )

    def test_household_query_single(self):
        self.snapshot_graphql_request(
            request_string=self.HOUSEHOLD_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(self.households[0].id, "Household")
            },
        )
