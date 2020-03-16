import io

from PIL import Image
from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    SimpleUploadedFile,
)

from account.fixtures import UserFactory
from core.base_test_case import APITestCase


class TestRegistrationDataImportDatahubQuery(APITestCase):
    multi_db = True

    UPLOAD_REGISTRATION_DATA_IMPORT_DATAHUB = """
    mutation UploadImportDataXLSXFile($file: Upload!) {
      uploadImportDataXlsxFile(file: $file) {
        importData {
          xlsxFile
          numberOfHouseholds
          numberOfIndividuals
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory()

        img = io.BytesIO(Image.new("RGB", (60, 30), color="red").tobytes())

        self.image = InMemoryUploadedFile(
            file=img,
            field_name="consent",
            name="consent.jpg",
            content_type="'image/jpeg'",
            size=(60, 30),
            charset=None,
        )

        self.xlsx_valid_file = (
            "hct_mis_api/apps/registration_datahub/tests/test_file/"
            "Registration Data Import XLS Template.xlsx"
        )

    def test_registration_data_import_datahub_upload(self):
        with open(self.xlsx_valid_file, "rb") as file:
            self.snapshot_graphql_request(
                request_string=self.UPLOAD_REGISTRATION_DATA_IMPORT_DATAHUB,
                context={"user": self.user},
                variables={"file": SimpleUploadedFile(file.name, file.read())},
            )
