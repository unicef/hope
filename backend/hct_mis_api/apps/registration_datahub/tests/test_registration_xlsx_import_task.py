import contextlib
from typing import Any
from unittest.mock import patch
from uuid import uuid4

from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    registration_xlsx_import_task,
)
from hct_mis_api.apps.registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
)
from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub


class TestRegistrationXlsxImportTask(TestCase):
    databases = {"default", "registration_datahub"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = BusinessAreaFactory()
        cls.rdi_datahub = RegistrationDataImportDatahubFactory()
        cls.program = ProgramFactory()

    @patch("hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create.RdiXlsxCreateTask.execute", return_value=None)
    def test_task_start_importing(self, _: Any) -> None:
        rdi = self._create_rdi_with_status(RegistrationDataImport.IMPORT_SCHEDULED)

        self._run_task()

        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.IMPORTING)

    def test_rdi_cannot_be_import_if_not_schedule_for_import(self) -> None:
        rdi = self._create_rdi_with_status(RegistrationDataImport.IMPORTING)

        self._run_task()

        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.IMPORTING)

    def test_only_one_task_for_the_same_rdi_could_be_run(self) -> None:
        rdi = self._create_rdi_with_status(RegistrationDataImport.IMPORTING)

        @contextlib.contextmanager
        def _mock(*args: Any, **kwargs: Any) -> Any:
            yield False

        with patch("hct_mis_api.apps.registration_datahub.celery_tasks.locked_cache", new=_mock):
            self._run_task()

        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.IMPORTING)

    def test_rdi_datahub_marked_as_dane_on_task_failed(self) -> None:
        self._create_rdi_with_status(RegistrationDataImport.IMPORT_SCHEDULED)

        def _mock(*args: Any, **kwargs: Any) -> None:
            raise Exception("something went wrong")

        with patch("hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create.RdiXlsxCreateTask.execute", new=_mock):
            with self.assertRaises(Exception) as context:
                self._run_task()

        self.assertEqual(str(context.exception), "something went wrong")
        self.rdi_datahub.refresh_from_db()
        self.assertEqual(self.rdi_datahub.import_done, RegistrationDataImportDatahub.DONE)

    def test_rdi_marked_as_import_error_on_task_failed(self) -> None:
        rdi = self._create_rdi_with_status(RegistrationDataImport.IMPORT_SCHEDULED)

        def _mock(*args: Any, **kwargs: Any) -> None:
            raise Exception("something went wrong")

        with patch("hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create.RdiXlsxCreateTask.execute", new=_mock):
            with self.assertRaises(Exception) as context:
                self._run_task()

        self.assertEqual(str(context.exception), "something went wrong")
        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.IMPORT_ERROR)

    def _run_task(self) -> None:
        registration_xlsx_import_task(
            registration_data_import_id=self.rdi_datahub.id,
            import_data_id=str(uuid4()),
            business_area_id=self.business_area.id,
            program_id=self.program.id,
        )

    def _create_rdi_with_status(self, status: str) -> RegistrationDataImport:
        return RegistrationDataImportFactory(
            status=status,
            datahub_id=self.rdi_datahub.id,
            business_area=self.business_area,
            program=self.program,
        )
