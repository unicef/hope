import io

from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from core.tests import APITestCase
from household.fixtures import RegistrationDataImportFactory


class TestHouseholdCreate(APITestCase):
    CREATE_HOUSEHOLD_MUTATION = """
    mutation CreateHousehold($householdData: CreateHouseholdInput) {
      createHousehold(householdData: $householdData) {
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
        self.location = LocationFactory.create()
        self.registration_data_import = RegistrationDataImportFactory.create()
        self.household_data = {
            'householdData': {
                'householdCaId': '2b7f0db7-9010-4d1d-8b1f-19357b29c7b0',
                'residenceStatus': 'REFUGEE',
                'nationality': 'AD',
                'familySize': 6,
                'address': 'this is my address',
                'locationId': self.id_to_base64(
                    self.location.id,
                    'Location',
                ),
                'registrationDataImportId': self.id_to_base64(
                    self.registration_data_import.id,
                    'RegistrationDataImport',
                ),
            }
        }

        img = Image.new('RGB', (60, 30), color='red')

        self.image = InMemoryUploadedFile(
            img,
            'consent',
            'consent.jpg',
            "'image/jpeg'",
            img.size,
            None,
        )

        self.file = io.BytesIO(b'Hello')

    def test_household_image_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_HOUSEHOLD_MUTATION,
            context={
                'user': self.user,
                'files': {'consent.jpg': self.image},
            },
            variables=self.household_data,
        )
    #
    # def test_household_image_not_authenticated(self):
    #     self.snapshot_graphql_request(
    #         request_string=self.CREATE_HOUSEHOLD_MUTATION,
    #         context={
    #             'files': {'consent.jpg': self.image},
    #         },
    #         variables=self.household_data,
    #     )
    #
    # def test_household_consent_validation_no_file(self):
    #     self.snapshot_graphql_request(
    #         request_string=self.CREATE_HOUSEHOLD_MUTATION,
    #         context={'user': self.user},
    #         variables=self.household_data,
    #     )
    #
    # def test_household_consent_validation_not_image(self):
    #     self.snapshot_graphql_request(
    #         request_string=self.CREATE_HOUSEHOLD_MUTATION,
    #         context={
    #             'user': self.user,
    #             'files': {'consent.jpg': self.file},
    #         },
    #         variables=self.household_data,
        )
