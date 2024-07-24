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
    databases = {"default", "registration_datahub"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.program = get_program_with_dct_type_and_name()
        cls.program_with_social_worker = get_program_with_dct_type_and_name(dct_type=DataCollectingType.Type.SOCIAL)

    @patch(
        "hct_mis_api.apps.registration_datahub.tasks.validate_xlsx_import.UploadXLSXInstanceValidator.validate_everything"
    )
    def test_people(self, validate_everything_mock: Mock) -> None:
        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/rdi_people_test.xlsx"
        ).read_bytes()
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
    def test_individuals(self, validate_everything_mock: Mock) -> None:
        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/new_reg_data_import.xlsx"
        ).read_bytes()
        file = File(BytesIO(content), name="new_reg_data_import.xlsx")
        import_data = ImportData.objects.create(
            file=file,
        )

        validate_everything_mock.return_value = [], []
        ValidateXlsxImport().execute(import_data, self.program)
        assert validate_everything_mock.call_count == 1

        import_data.refresh_from_db()
        assert import_data.status == ImportData.STATUS_FINISHED
        assert import_data.number_of_households == 3
        assert import_data.number_of_individuals == 7

        validate_everything_mock.reset_mock()
        validate_everything_mock.return_value = [
            {
                "row_number": 1,
                "header": "First Name",
                "error": "First Name is required",
            }
        ], [
            {
                "row_number": 2,
                "header": "Last Name",
                "error": "Last Name is required",
            }
        ]
        ValidateXlsxImport().execute(import_data, self.program)
        assert validate_everything_mock.call_count == 1
        assert import_data.status == ImportData.STATUS_VALIDATION_ERROR

        validate_everything_mock.reset_mock()
        validate_everything_mock.return_value = [], [
            {
                "row_number": 2,
                "header": "Last Name",
                "error": "Last Name is required",
            }
        ]
        ValidateXlsxImport().execute(import_data, self.program)
        assert validate_everything_mock.call_count == 1
        assert import_data.status == ImportData.STATUS_DELIVERY_MECHANISMS_VALIDATION_ERROR
