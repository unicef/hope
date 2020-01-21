from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import LocationFactory


class TestUpdateLocation(APITestCase):
    UPDATE_LOCATION_MUTATION = """
    mutation UpdateLocation($locationData: UpdateLocationInput) {
      updateLocation(locationData: $locationData) {
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
        self.location = LocationFactory.create()
        self.location_data = {
            'locationData': {
                'id': self.id_to_base64(self.location.id, 'Location'),
                'name': 'Test Location',
                'country': 'PL',
            }
        }

    def test_update_location_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.UPDATE_LOCATION_MUTATION,
            variables=self.location_data,
        )

    def test_update_location_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.UPDATE_LOCATION_MUTATION,
            context={'user': self.user},
            variables=self.location_data,
        )
