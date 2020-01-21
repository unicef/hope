from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from household.fixtures import HouseholdFactory
from household.models import Household


class TestDeleteHousehold(APITestCase):
    DELETE_PROGRAM_MUTATION = """
    mutation DeleteHousehold($householdId: String!) {
      deleteHousehold(householdId: $householdId) {
            ok
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.household = HouseholdFactory.create()

    def test_delete_household_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            variables={
                'householdId': self.id_to_base64(self.household.id, 'Household')
            },
        )

    def test_delete_household_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.DELETE_PROGRAM_MUTATION,
            context={'user': self.user},
            variables={
                'householdId': self.id_to_base64(self.household.id, 'Household')
            },
        )

        assert not Household.objects.filter(id=self.household.id).exists()
