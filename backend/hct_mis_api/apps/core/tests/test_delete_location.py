import unittest

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import LocationFactory
from core.models import Location


@unittest.skip("Not supporting locations")
class TestDeleteLocation(APITestCase):
    DELETE_LOCATION_MUTATION = """
    mutation DeleteLocation($locationId: String!) {
      deleteLocation(locationId: $locationId) {
        ok
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.location = LocationFactory.create()

    def test_delete_location_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.DELETE_LOCATION_MUTATION,
            variables={
                "locationId": self.id_to_base64(self.location.id, "Location"),
            },
        )

    def test_delete_location_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.DELETE_LOCATION_MUTATION,
            context={"user": self.user},
            variables={
                "locationId": self.id_to_base64(self.location.id, "Location"),
            },
        )

        assert not Location.objects.filter(id=self.location.id).exists()
