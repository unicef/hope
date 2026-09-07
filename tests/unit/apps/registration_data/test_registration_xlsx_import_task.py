from collections.abc import Callable
from typing import Any
from unittest.mock import patch
from uuid import uuid4

from django.core.cache import cache
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.celery_lock import AlreadyRunningError, lock_key
from hope.apps.registration_data.celery_tasks import (
    registration_xlsx_import_async_task,
    registration_xlsx_import_async_task_action,
)
from hope.models import AsyncRetryJob, RegistrationDataImport


@pytest.fixture
def hold_lock(monkeypatch: pytest.MonkeyPatch) -> Callable[..., None]:
    monkeypatch.setattr("hope.apps.core.celery_lock.LOCK_WAIT", 0)

    def _hold(task: str, *parts: object) -> None:
        cache.lock(lock_key(task, *parts)).acquire()

    return _hold


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area)


def run_registration_xlsx_import_task(
    registration_data_import_id: str,
    import_data_id: str,
    business_area_id: str,
    program_id: str,
) -> bool:
    job = AsyncRetryJob(
        config={
            "registration_data_import_id": registration_data_import_id,
            "import_data_id": import_data_id,
            "business_area_id": str(business_area_id),
            "program_id": str(program_id),
        }
    )
    return registration_xlsx_import_async_task_action(job)


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

    run_registration_xlsx_import_task(
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

    run_registration_xlsx_import_task(
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
    hold_lock: Callable[..., None],
) -> None:
    rdi = RegistrationDataImportFactory(
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        business_area=business_area,
        program=program,
    )
    hold_lock("registration_xlsx_import", rdi.id)

    with patch("hope.apps.registration_data.tasks.rdi_xlsx_create.RdiXlsxCreateTask.execute") as mock_execute:
        with pytest.raises(AlreadyRunningError, match=f"celery_lock_registration_xlsx_import:{rdi.id}"):
            run_registration_xlsx_import_task(
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
            run_registration_xlsx_import_task(
                registration_data_import_id=str(rdi.id),
                import_data_id=str(uuid4()),
                business_area_id=business_area.id,
                program_id=program.id,
            )

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IMPORT_ERROR


def test_registration_xlsx_import_task_queues_retry_job(
    business_area: Any, program: Any, django_capture_on_commit_callbacks
) -> None:
    rdi = RegistrationDataImportFactory(
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        business_area=business_area,
        program=program,
    )
    import_data_id = str(uuid4())

    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        with django_capture_on_commit_callbacks(execute=True):
            registration_xlsx_import_async_task(
                registration_data_import=rdi,
                import_data_id=str(import_data_id),
                business_area_id=str(business_area.id),
                program_id=str(program.id),
            )

    job = AsyncRetryJob.objects.latest("pk")
    assert job.content_object == rdi
    assert job.action == "hope.apps.registration_data.celery_tasks.registration_xlsx_import_async_task_action"
    assert job.config == {
        "registration_data_import_id": str(rdi.id),
        "import_data_id": str(import_data_id),
        "business_area_id": str(business_area.id),
        "program_id": str(program.id),
    }
    mock_queue.assert_called_once()
