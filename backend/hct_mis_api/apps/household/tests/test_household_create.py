import io
import sys

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import LocationFactory
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
            "householdData": {
                "householdCaId": "2b7f0db7-9010-4d1d-8b1f-19357b29c7b0",
                "residenceStatus": "REFUGEE",
                "nationality": "AD",
                "familySize": 6,
                "address": "this is my address",
                "locationId": self.id_to_base64(self.location.id, "Location",),
                "registrationDataImportId": self.id_to_base64(
                    self.registration_data_import.id, "RegistrationDataImport",
                ),
            }
        }

        img = io.BytesIO(Image.new("RGB", (60, 30), color="red").tobytes())

        self.image = InMemoryUploadedFile(
            file=img,
            field_name="consent",
            name="consent.jpg",
            content_type="'image/jpeg'",
            size=(60, 30),
            charset=None,
        )

        text_file = io.BytesIO(b"Hello")

        self.file = InMemoryUploadedFile(
            file=text_file,
            field_name="consent",
            name="consent.txt",
            content_type="'text/plain'",
            size=sys.getsizeof(text_file),
            charset=None,
        )

    def test_household_create_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_HOUSEHOLD_MUTATION,
            context={"user": self.user, "files": {"1": self.image},},
            variables=self.household_data,
        )

    def test_household_create_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_HOUSEHOLD_MUTATION,
            context={"files": {"1": self.image},},
            variables=self.household_data,
        )

    def test_household_consent_validation_no_file(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_HOUSEHOLD_MUTATION,
            context={"user": self.user},
            variables=self.household_data,
        )

    def test_household_consent_validation_not_image(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_HOUSEHOLD_MUTATION,
            context={"user": self.user, "files": {"1": self.file},},
            variables=self.household_data,
        )
