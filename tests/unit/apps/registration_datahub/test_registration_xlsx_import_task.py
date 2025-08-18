import contextlib
from typing import Any
from unittest.mock import patch
from uuid import uuid4

from django.test import TestCase

from extras.test_utils.factories.account import BusinessAreaFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory

from hope.apps.registration_data.models import RegistrationDataImport
from hope.apps.registration_datahub.celery_tasks import (
    registration_xlsx_import_task,
)


class TestRegistrationXlsxImportTask(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = BusinessAreaFactory()
        cls.program = ProgramFactory()

    @patch("hope.apps.registration_datahub.tasks.rdi_xlsx_create.RdiXlsxCreateTask.execute", return_value=None)
    def test_task_start_importing(self, _: Any) -> None:
        rdi = self._create_rdi_with_status(RegistrationDataImport.IMPORT_SCHEDULED)

        self._run_task(rdi.id)

        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.IMPORTING

    def test_rdi_cannot_be_import_if_not_schedule_for_import(self) -> None:
        rdi = self._create_rdi_with_status(RegistrationDataImport.IMPORTING)

        self._run_task(rdi.id)

        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.IMPORTING

    def test_only_one_task_for_the_same_rdi_could_be_run(self) -> None:
        rdi = self._create_rdi_with_status(RegistrationDataImport.IMPORTING)

        @contextlib.contextmanager
        def _mock(*args: Any, **kwargs: Any) -> Any:
            yield False

        with patch("hope.apps.registration_datahub.celery_tasks.locked_cache", new=_mock):
            self._run_task(rdi.id)

        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.IMPORTING

    def test_rdi_marked_as_import_error_on_task_failed(self) -> None:
        rdi = self._create_rdi_with_status(RegistrationDataImport.IMPORT_SCHEDULED)

        def _mock(*args: Any, **kwargs: Any) -> None:
            raise Exception("something went wrong")

        with patch("hope.apps.registration_datahub.tasks.rdi_xlsx_create.RdiXlsxCreateTask.execute", new=_mock):
            with self.assertRaises(Exception) as context:
                self._run_task(rdi.id)

        assert str(context.exception) == "something went wrong"

    def _run_task(self, rdi_id: str) -> None:
        registration_xlsx_import_task(
            registration_data_import_id=rdi_id,
            import_data_id=str(uuid4()),
            business_area_id=self.business_area.id,
            program_id=self.program.id,
        )

    def _create_rdi_with_status(self, status: str) -> RegistrationDataImport:
        return RegistrationDataImportFactory(
            status=status,
            business_area=self.business_area,
            program=self.program,
        )
