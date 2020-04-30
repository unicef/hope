import io
import unittest

from PIL import Image
from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    SimpleUploadedFile,
)
from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from registration_data.fixtures import RegistrationDataImportFactory
from registration_datahub.fixtures import (
    ImportedIndividualFactory,
    ImportedHouseholdFactory,
    RegistrationDataImportDatahubFactory,
)
from registration_datahub.models import ImportData


class TestRegistrationDataImportDatahubMutations(APITestCase):
    multi_db = True

    UPLOAD_REGISTRATION_DATA_IMPORT_DATAHUB = """
    mutation UploadImportDataXLSXFile($file: Upload!) {
      uploadImportDataXlsxFile(file: $file) {
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
    mutation CreateRegistrationDataImport(
      $registrationDataImportData: CreateRegistrationDataImportExcelInput!
    ) {
      createRegistrationDataImport(
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

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        call_command("loadbusinessareas")

        img = io.BytesIO(Image.new("RGB", (60, 30), color="red").tobytes())

        self.image = InMemoryUploadedFile(
            file=img,
            field_name="consent",
            name="consent.jpg",
            content_type="'image/jpeg'",
            size=(60, 30),
            charset=None,
        )

        xlsx_valid_file_path = "hct_mis_api/apps/registration_datahub/tests/test_file/new_reg_data_import.xlsx"

        with open(xlsx_valid_file_path, "rb") as file:
            self.valid_file = SimpleUploadedFile(file.name, file.read())

    def test_registration_data_import_datahub_upload(self):
        self.snapshot_graphql_request(
            request_string=self.UPLOAD_REGISTRATION_DATA_IMPORT_DATAHUB,
            context={"user": self.user},
            variables={"file": self.valid_file},
        )

        import_data_obj = ImportData.objects.first()
        self.assertIn(
            "new_reg_data_import", import_data_obj.xlsx_file.name,
        )

    def test_registration_data_import_create(self):
        import_data_obj = ImportData.objects.create(
            xlsx_file=self.valid_file,
            number_of_households=500,
            number_of_individuals=1000,
        )

        self.snapshot_graphql_request(
            request_string=self.CREATE_REGISTRATION_DATA_IMPORT,
            context={"user": self.user},
            variables={
                "registrationDataImportData": {
                    "importDataId": self.id_to_base64(
                        import_data_obj.id, "ImportData"
                    ),
                    "name": "New Import of Data 123",
                    "businessAreaSlug": "afghanistan",
                }
            },
        )

    def test_approve_registration_data_import(self):
        registration_data_import_obj = RegistrationDataImportFactory(
            status="IN_REVIEW",
        )

        self.snapshot_graphql_request(
            request_string=self.APPROVE_REGISTRATION_DATA_IMPORT,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    registration_data_import_obj.id, "RegistrationDataImport",
                )
            },
        )

    def test_approve_registration_data_import_wrong_initial_status(self):
        registration_data_import_obj = RegistrationDataImportFactory(
            status="APPROVED",
        )

        self.snapshot_graphql_request(
            request_string=self.APPROVE_REGISTRATION_DATA_IMPORT,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    registration_data_import_obj.id, "RegistrationDataImport",
                )
            },
        )

    def test_unapprove_registration_data_import_wrong_initial_status(self):
        registration_data_import_obj = RegistrationDataImportFactory(
            status="MERGED",
        )

        self.snapshot_graphql_request(
            request_string=self.UNAPPROVE_REGISTRATION_DATA_IMPORT,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    registration_data_import_obj.id, "RegistrationDataImport",
                )
            },
        )

    def test_unapprove_registration_data_import(self):
        registration_data_import_obj = RegistrationDataImportFactory(
            status="APPROVED",
        )

        self.snapshot_graphql_request(
            request_string=self.UNAPPROVE_REGISTRATION_DATA_IMPORT,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    registration_data_import_obj.id, "RegistrationDataImport",
                )
            },
        )

    @unittest.skip("Work in progress")
    def test_merge_registration_data_import(self):
        obj_hct = RegistrationDataImportFactory.build(
            name="Lorem Ipsum", status="APPROVED", imported_by=self.user,
        )
        obj_datahub = RegistrationDataImportDatahubFactory.build(
            name="Lorem Ipsum", hct_id=obj_hct.id,
        )

        obj_hct.datahub_id = obj_datahub.id
        obj_hct.save()
        obj_datahub.save()

        for _ in range(350):
            imported_household = ImportedHouseholdFactory(
                registration_data_import=obj_datahub,
            )
            individuals = ImportedIndividualFactory.create_batch(
                imported_household.family_size,
                registration_data_import=obj_datahub,
            )
            imported_household.head_of_household = individuals[0]
            imported_household.representative = individuals[0]
            imported_household.save()

        self.snapshot_graphql_request(
            request_string=self.MERGE_REGISTRATION_DATA_IMPORT,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(obj_hct.id, "RegistrationDataImport",)
            },
        )
