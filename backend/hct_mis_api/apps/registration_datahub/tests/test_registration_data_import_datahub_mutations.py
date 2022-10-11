import io

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile

from parameterized import parameterized
from PIL import Image

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_datahub.models import ImportData


class TestRegistrationDataImportDatahubMutations(APITestCase):
    databases = "__all__"

    UPLOAD_REGISTRATION_DATA_IMPORT_DATAHUB = """
    mutation UploadImportDataXLSXFile(
      $file: Upload!, $businessAreaSlug: String!
    ) {
      uploadImportDataXlsxFileAsync(
        file: $file, businessAreaSlug: $businessAreaSlug
      ) {
        importData {
          numberOfHouseholds
          numberOfIndividuals
        }
        errors {
          rowNumber
          header
          message
        }
      }
    }
    """

    CREATE_REGISTRATION_DATA_IMPORT = """
    mutation RegistrationXlsxImportMutation(
      $registrationDataImportData: RegistrationXlsxImportMutationInput!
    ) {
      registrationXlsxImport(
        registrationDataImportData: $registrationDataImportData
      ) {
        registrationDataImport {
          name
          status
          numberOfHouseholds
          numberOfIndividuals
        }
      }
    }
    """

    APPROVE_REGISTRATION_DATA_IMPORT = """
    mutation ApproveRegistrationDataImportMutation($id: ID!) {
      approveRegistrationDataImport(id: $id) {
        registrationDataImport {
          status
        }
      }
    }
    """

    UNAPPROVE_REGISTRATION_DATA_IMPORT = """
    mutation UnapproveRegistrationDataImportMutation($id: ID!) {
      unapproveRegistrationDataImport(id: $id) {
        registrationDataImport {
          status
        }
      }
    }
    """

    MERGE_REGISTRATION_DATA_IMPORT = """
    mutation MergeRegistrationDataImportMutation($id: ID!) {
      mergeRegistrationDataImport(id: $id) {
        registrationDataImport {
          status
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        create_afghanistan()
        cls.business_area_slug = "afghanistan"
        cls.business_area = BusinessArea.objects.get(slug=cls.business_area_slug)

        img = io.BytesIO(Image.new("RGB", (60, 30), color="red").tobytes())

        cls.image = InMemoryUploadedFile(
            file=img,
            field_name="consent",
            name="consent.jpg",
            content_type="'image/jpeg'",
            size=(60, 30),
            charset=None,
        )

        xlsx_valid_file_path = (
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/new_reg_data_import.xlsx"
        )

        with open(xlsx_valid_file_path, "rb") as file:
            cls.valid_file = SimpleUploadedFile(file.name, file.read())

    @parameterized.expand(
        [
            ("with_permission", [Permissions.RDI_IMPORT_DATA], True),
            ("without_permission", [], False),
        ]
    )
    def test_registration_data_import_datahub_upload(self, _, permissions, should_have_import_data):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.UPLOAD_REGISTRATION_DATA_IMPORT_DATAHUB,
            context={"user": self.user},
            variables={"file": self.valid_file, "businessAreaSlug": self.business_area_slug},
        )

        if should_have_import_data:
            import_data_obj = ImportData.objects.first()
            self.assertIn(
                "new_reg_data_import",
                import_data_obj.file.name,
            )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.RDI_IMPORT_DATA],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_registration_data_import_create(self, _, permissions):
        import_data_obj = ImportData.objects.create(
            file=self.valid_file,
            number_of_households=3,
            number_of_individuals=6,
        )
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.CREATE_REGISTRATION_DATA_IMPORT,
            context={"user": self.user},
            variables={
                "registrationDataImportData": {
                    "importDataId": self.id_to_base64(import_data_obj.id, "ImportDataNode"),
                    "name": "New Import of Data 123",
                    "businessAreaSlug": self.business_area_slug,
                }
            },
        )
