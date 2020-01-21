from account.fixtures import UserFactory
from core.base_test_case import APITestCase


class TestCreateLocation(APITestCase):

    CREATE_LOCATION_MUTATION = """
    mutation CreateLocation($locationData: CreateLocationInput!) {
      createLocation(locationData: $locationData) {
        location {
          name
          country
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.location_data = {
            'locationData': {
                'name': 'Test Location',
                'country': 'PL',
            }
        }

    def test_create_location_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_LOCATION_MUTATION,
            variables=self.location_data,
        )

    def test_create_location_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_LOCATION_MUTATION,
            context={'user': self.user},
            variables=self.location_data,
        )
