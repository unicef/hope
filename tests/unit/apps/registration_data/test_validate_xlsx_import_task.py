from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

from django.core.files import File
import pytest

from extras.test_utils.factories.core import BeneficiaryGroupFactory, BusinessAreaFactory, DataCollectingTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import ImportDataFactory
from hope.apps.registration_data.tasks.validate_xlsx_import import ValidateXlsxImport
from hope.models import DataCollectingType, ImportData

pytestmark = pytest.mark.django_db

FILES_DIR = Path(__file__).resolve().parent / "test_file"


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_with_social_worker(business_area: Any) -> Any:
    data_collecting_type = DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL)
    beneficiary_group = BeneficiaryGroupFactory(master_detail=False)
    return ProgramFactory(
        business_area=business_area,
        data_collecting_type=data_collecting_type,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def import_data(business_area: Any) -> ImportData:
    content = (FILES_DIR / "new_reg_data_import.xlsx").read_bytes()
    file = File(BytesIO(content), name="new_reg_data_import.xlsx")
    return ImportDataFactory(file=file, business_area_slug=business_area.slug)


@pytest.fixture
def import_data_people(business_area: Any) -> ImportData:
    content = (FILES_DIR / "rdi_people_test.xlsx").read_bytes()
    file = File(BytesIO(content), name="rdi_people_test.xlsx")
    return ImportDataFactory(file=file, business_area_slug=business_area.slug)


@patch("hope.apps.registration_data.tasks.validate_xlsx_import.UploadXLSXInstanceValidator.validate_everything")
def test_people(
    validate_everything_mock: Mock,
    import_data_people: ImportData,
    program_with_social_worker: Any,
) -> None:
    validate_everything_mock.return_value = []
    ValidateXlsxImport().execute(import_data_people, program_with_social_worker)
    assert validate_everything_mock.call_count == 1

    import_data_people.refresh_from_db()
    assert import_data_people.status == ImportData.STATUS_FINISHED
    assert import_data_people.number_of_households == 0
    assert import_data_people.number_of_individuals == 5


@patch("hope.apps.registration_data.tasks.validate_xlsx_import.UploadXLSXInstanceValidator.validate_everything")
def test_import_individuals_without_errors(
    validate_everything_mock: Mock,
    import_data: ImportData,
    program: Any,
) -> None:
    validate_everything_mock.return_value = []
    ValidateXlsxImport().execute(import_data, program)
    assert validate_everything_mock.call_count == 1

    import_data.refresh_from_db()
    assert import_data.status == ImportData.STATUS_FINISHED
    assert import_data.number_of_households == 3
    assert import_data.number_of_individuals == 7


@patch("hope.apps.registration_data.tasks.validate_xlsx_import.UploadXLSXInstanceValidator.validate_everything")
def test_import_individuals_with_errors(
    validate_everything_mock: Mock,
    import_data: ImportData,
    program: Any,
) -> None:
    validate_everything_mock.return_value = [
        {
            "row_number": 1,
            "header": "First Name",
            "error": "First Name is required",
        }
    ]
    ValidateXlsxImport().execute(import_data, program)
    assert validate_everything_mock.call_count == 1
    assert import_data.status == ImportData.STATUS_VALIDATION_ERROR


@patch("hope.apps.registration_data.tasks.validate_xlsx_import.UploadXLSXInstanceValidator.validate_everything")
def test_import_individuals_with_general_errors(
    validate_everything_mock: Mock,
    import_data: ImportData,
    program: Any,
) -> None:
    validate_everything_mock.return_value = [
        {
            "row_number": 1,
            "header": "First Name",
            "error": "First Name is required",
        }
    ]
    ValidateXlsxImport().execute(import_data, program)
    assert validate_everything_mock.call_count == 1
    assert import_data.status == ImportData.STATUS_VALIDATION_ERROR
