from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

from django.conf import settings
from django.core.files import File
from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.program.fixtures import get_program_with_dct_type_and_name
from hct_mis_api.apps.registration_data.models import ImportData
from hct_mis_api.apps.registration_datahub.tasks.validate_xlsx_import import (
    ValidateXlsxImport,
)


class TestValidateXlsxImportTask(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.program = get_program_with_dct_type_and_name()
        cls.program_with_social_worker = get_program_with_dct_type_and_name(dct_type=DataCollectingType.Type.SOCIAL)

        content = Path(
            f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/new_reg_data_import.xlsx"
        ).read_bytes()
        file = File(BytesIO(content), name="new_reg_data_import.xlsx")
        cls.import_data = ImportData.objects.create(
            file=file,
        )

    @patch(
        "hct_mis_api.apps.registration_datahub.tasks.validate_xlsx_import.UploadXLSXInstanceValidator.validate_everything"
    )
    def test_people(self, validate_everything_mock: Mock) -> None:
        content = Path(f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/rdi_people_test.xlsx").read_bytes()
        file = File(BytesIO(content), name="rdi_people_test.xlsx")
        import_data = ImportData.objects.create(
            file=file,
        )

        validate_everything_mock.return_value = [], []
        ValidateXlsxImport().execute(import_data, self.program_with_social_worker)
        assert validate_everything_mock.call_count == 1

        import_data.refresh_from_db()
        assert import_data.status == ImportData.STATUS_FINISHED
        assert import_data.number_of_households == 0
        assert import_data.number_of_individuals == 4

    @patch(
        "hct_mis_api.apps.registration_datahub.tasks.validate_xlsx_import.UploadXLSXInstanceValidator.validate_everything"
    )
    def test_import_individuals_without_errors(self, validate_everything_mock: Mock) -> None:
        validate_everything_mock.return_value = [], []
        ValidateXlsxImport().execute(self.import_data, self.program)
        assert validate_everything_mock.call_count == 1

        self.import_data.refresh_from_db()
        assert self.import_data.status == ImportData.STATUS_FINISHED
        assert self.import_data.number_of_households == 3
        assert self.import_data.number_of_individuals == 7

    @patch(
        "hct_mis_api.apps.registration_datahub.tasks.validate_xlsx_import.UploadXLSXInstanceValidator.validate_everything"
    )
    def test_import_individuals_with_errors(self, validate_everything_mock: Mock) -> None:
        validate_everything_mock.return_value = [
            {
                "row_number": 1,
                "header": "First Name",
                "error": "First Name is required",
            }
        ], [
            {
                "header": "name_of_cardholder__atm_card_i_c",
                "message": "Field name_of_cardholder__atm_card_i_c is required for delivery " "mechanism ATM Card",
                "row_number": 2,
            },
        ]
        ValidateXlsxImport().execute(self.import_data, self.program)
        assert validate_everything_mock.call_count == 1
        assert self.import_data.status == ImportData.STATUS_VALIDATION_ERROR

    @patch(
        "hct_mis_api.apps.registration_datahub.tasks.validate_xlsx_import.UploadXLSXInstanceValidator.validate_everything"
    )
    def test_import_individuals_with_general_errors(self, validate_everything_mock: Mock) -> None:
        validate_everything_mock.return_value = [
            {
                "row_number": 1,
                "header": "First Name",
                "error": "First Name is required",
            }
        ], []
        ValidateXlsxImport().execute(self.import_data, self.program)
        assert validate_everything_mock.call_count == 1
        assert self.import_data.status == ImportData.STATUS_VALIDATION_ERROR

    @patch(
        "hct_mis_api.apps.registration_datahub.tasks.validate_xlsx_import.UploadXLSXInstanceValidator.validate_everything"
    )
    def test_import_individuals_with_delivery_mechanisms_errors(self, validate_everything_mock: Mock) -> None:
        validate_everything_mock.return_value = [], [
            {
                "header": "name_of_cardholder__atm_card_i_c",
                "message": "Field name_of_cardholder__atm_card_i_c is required for delivery " "mechanism ATM Card",
                "row_number": 2,
            },
        ]
        ValidateXlsxImport().execute(self.import_data, self.program)
        assert validate_everything_mock.call_count == 1
        assert self.import_data.status == ImportData.STATUS_DELIVERY_MECHANISMS_VALIDATION_ERROR
