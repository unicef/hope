import contextlib
from typing import Any
from unittest.mock import patch
from uuid import uuid4

import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.registration_data.celery_tasks import registration_xlsx_import_task
from hope.models import RegistrationDataImport


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area)


@patch(
    "hope.apps.registration_data.tasks.rdi_xlsx_create.RdiXlsxCreateTask.execute",
    return_value=None,
)
def test_task_start_importing(
    mock_execute: Any,
    business_area: Any,
    program: Any,
) -> None:
    rdi = RegistrationDataImportFactory(
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        business_area=business_area,
        program=program,
    )

    registration_xlsx_import_task(
        registration_data_import_id=str(rdi.id),
        import_data_id=str(uuid4()),
        business_area_id=business_area.id,
        program_id=program.id,
    )

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IMPORTING


def test_rdi_cannot_be_import_if_not_schedule_for_import(
    business_area: Any,
    program: Any,
) -> None:
    rdi = RegistrationDataImportFactory(
        status=RegistrationDataImport.LOADING,
        business_area=business_area,
        program=program,
    )

    registration_xlsx_import_task(
        registration_data_import_id=str(rdi.id),
        import_data_id=str(uuid4()),
        business_area_id=business_area.id,
        program_id=program.id,
    )

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.LOADING


def test_only_one_task_for_the_same_rdi_could_be_run(
    business_area: Any,
    program: Any,
) -> None:
    rdi = RegistrationDataImportFactory(
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        business_area=business_area,
        program=program,
    )

    @contextlib.contextmanager
    def _mock(*args: Any, **kwargs: Any) -> Any:
        yield False

    with patch("hope.apps.registration_data.celery_tasks.locked_cache", new=_mock):
        with patch("hope.apps.registration_data.tasks.rdi_xlsx_create.RdiXlsxCreateTask.execute") as mock_execute:
            registration_xlsx_import_task(
                registration_data_import_id=str(rdi.id),
                import_data_id=str(uuid4()),
                business_area_id=business_area.id,
                program_id=program.id,
            )
            mock_execute.assert_not_called()

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED


def test_rdi_marked_as_import_error_on_task_failed(
    business_area: Any,
    program: Any,
) -> None:
    rdi = RegistrationDataImportFactory(
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        business_area=business_area,
        program=program,
    )

    def _mock(*args: Any, **kwargs: Any) -> None:
        raise Exception("something went wrong")

    with patch(
        "hope.apps.registration_data.tasks.rdi_xlsx_create.RdiXlsxCreateTask.execute",
        new=_mock,
    ):
        with pytest.raises(Exception, match="something went wrong"):
            registration_xlsx_import_task(
                registration_data_import_id=str(rdi.id),
                import_data_id=str(uuid4()),
                business_area_id=business_area.id,
                program_id=program.id,
            )

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IMPORT_ERROR
