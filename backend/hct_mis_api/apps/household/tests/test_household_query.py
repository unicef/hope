from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from household.fixtures import HouseholdFactory


class TestHouseholdQuery(APITestCase):
    ALL_HOUSEHOLD_QUERY = """
    query AllHouseholds{
      allHouseholds {
        edges {
          node {
            familySize
            nationality
            householdCaId
            address
          }
        }
      }
    }
    """
    ALL_HOUSEHOLD_QUERY_RANGE = """
    query AllHouseholds{
      allHouseholds(familySize: "{\\"min\\": 3, \\"max\\": 9}") {
        edges {
          node {
            familySize
            nationality
            householdCaId
            address
          }
        }
      }
    }
    """
    ALL_HOUSEHOLD_QUERY_MIN = """
    query AllHouseholds{
      allHouseholds(familySize: "{\\"min\\": 3}") {
        edges {
          node {
            familySize
            nationality
            householdCaId
            address
          }
        }
      }
    }
    """
    ALL_HOUSEHOLD_QUERY_MAX = """
    query AllHouseholds{
      allHouseholds(familySize: "{\\"max\\": 9}") {
        edges {
          node {
            familySize
            nationality
            householdCaId
            address
          }
        }
      }
    }
    """
    HOUSEHOLD_QUERY = """
    query Household($id: ID!) {
      household(id: $id) {
        familySize
        nationality
        householdCaId
        address
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        family_sizes_list = (2, 4, 5, 1, 3, 11, 14)
        self.households = [
            HouseholdFactory(
                family_size=family_size,
                address="Lorem Ipsum",
                nationality="PL",
                household_ca_id="123-123-123",
            )
            for family_size in family_sizes_list
        ]

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

    def test_household_query_single(self):
        self.snapshot_graphql_request(
            request_string=self.HOUSEHOLD_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.households[0].id, "Household"
                )
            },
        )
