import io
import sys

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from core.tests import APITestCase
from household.fixtures import HouseholdFactory


class TestHouseholdUpdate(APITestCase):
    CREATE_HOUSEHOLD_MUTATION = """
    mutation UpdateHousehold($householdData: UpdateHouseholdInput) {
      updateHousehold(householdData: $householdData) {
        household {
          familySize
          address
          nationality
          residenceStatus
          householdCaId
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.household = HouseholdFactory()
        self.household_data = {
            'householdData': {
                'id': self.id_to_base64(self.household.id, 'Household'),
                'householdCaId': '2b7f0db7-9010-4d1d-8b1f-19357b29c7b0',
                'residenceStatus': 'REFUGEE',
                'nationality': 'AD',
                'familySize': 6,
                'address': 'this is my address',
            }
        }

    def test_household_update_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_HOUSEHOLD_MUTATION,
            context={
                'user': self.user,
            },
            variables=self.household_data,
        )

    def test_household_update_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_HOUSEHOLD_MUTATION,
            variables=self.household_data,
        )
