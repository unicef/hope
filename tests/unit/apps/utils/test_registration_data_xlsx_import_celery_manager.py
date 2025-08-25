from unittest import mock

from django.core.management import call_command
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory

from hope.apps.core.base_test_case import BaseTestCase
from models.core import BusinessArea
from models.registration_data import ImportData, RegistrationDataImport


class TestRegistrationDataXlsxImportCeleryManager(BaseTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadbusinessareas")

    @mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
    def test_querysets(self, _: mock.MagicMock) -> None:
        from hope.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        manager = RegistrationDataXlsxImportCeleryManager()
        program = ProgramFactory()
        rdi_import_scheduled = RegistrationDataImportFactory(
            name="IMPORT_SCHEDULED",
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            data_source=RegistrationDataImport.XLS,
            program=program,
        )
        rdi_importing = RegistrationDataImportFactory(
            name="IMPORTING",
            status=RegistrationDataImport.IMPORTING,
            data_source=RegistrationDataImport.XLS,
            program=program,
        )
        RegistrationDataImportFactory(
            name="IMPORT_ERROR",
            status=RegistrationDataImport.IMPORT_ERROR,
            data_source=RegistrationDataImport.XLS,
            program=program,
        )
        RegistrationDataImportFactory(
            name="REFUSED_IMPORT",
            status=RegistrationDataImport.REFUSED_IMPORT,
            data_source=RegistrationDataImport.XLS,
            program=program,
        )
        RegistrationDataImportFactory(
            name="DEDUPLICATION",
            status=RegistrationDataImport.DEDUPLICATION,
            data_source=RegistrationDataImport.XLS,
            program=program,
        )
        RegistrationDataImportFactory(
            name="DEDUPLICATION_FAILED",
            status=RegistrationDataImport.DEDUPLICATION_FAILED,
            data_source=RegistrationDataImport.XLS,
            program=program,
        )
        RegistrationDataImportFactory(
            name="MERGE_SCHEDULED",
            status=RegistrationDataImport.MERGE_SCHEDULED,
            data_source=RegistrationDataImport.XLS,
            program=program,
        )
        RegistrationDataImportFactory(
            name="MERGING",
            status=RegistrationDataImport.MERGING,
            data_source=RegistrationDataImport.XLS,
            program=program,
        )
        RegistrationDataImportFactory(
            name="MERGE_ERROR",
            status=RegistrationDataImport.MERGE_ERROR,
            data_source=RegistrationDataImport.XLS,
            program=program,
        )
        RegistrationDataImportFactory(
            name="MERGED",
            status=RegistrationDataImport.MERGED,
            data_source=RegistrationDataImport.XLS,
            program=program,
        )
        assert manager.pending_queryset.count() == 1
        assert manager.pending_queryset.first() == rdi_import_scheduled
        assert manager.in_progress_queryset.count() == 1
        assert manager.in_progress_queryset.first() == rdi_importing

    @mock.patch("hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
    @mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
    def test_add_scheduled_to_queue(
        self,
        mock_get_all_celery_tasks: mock.MagicMock,
        mock_registration_xlsx_import_task_delay: mock.MagicMock,
    ) -> None:
        from hope.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        mock_get_all_celery_tasks.return_value = []
        program = ProgramFactory()

        import_data = ImportData.objects.create()
        rdi = RegistrationDataImportFactory(
            name="IMPORT_SCHEDULED",
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            data_source=RegistrationDataImport.XLS,
            program=program,
            import_data=import_data,
        )
        manager = RegistrationDataXlsxImportCeleryManager()
        manager.execute()
        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
        assert mock_registration_xlsx_import_task_delay.call_count == 1
        mock_registration_xlsx_import_task_delay.assert_called_with(
            registration_data_import_id=str(rdi.id),
            import_data_id=str(rdi.import_data_id),
            business_area_id=str(rdi.business_area_id),
            program_id=str(rdi.program_id),
        )

    @mock.patch("hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
    @mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
    def test_revert_status_rdi_with_importing_status(
        self,
        mock_get_all_celery_tasks: mock.MagicMock,
        mock_registration_xlsx_import_task_delay: mock.MagicMock,
    ) -> None:
        from hope.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        mock_get_all_celery_tasks.return_value = []
        program = ProgramFactory()

        import_data = ImportData.objects.create()
        rdi = RegistrationDataImportFactory(
            name="IMPORTING",
            status=RegistrationDataImport.IMPORTING,
            data_source=RegistrationDataImport.XLS,
            program=program,
            import_data=import_data,
        )
        manager = RegistrationDataXlsxImportCeleryManager()
        manager.execute()
        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
        assert mock_registration_xlsx_import_task_delay.call_count == 1
        mock_registration_xlsx_import_task_delay.assert_called_with(
            registration_data_import_id=str(rdi.id),
            import_data_id=str(rdi.import_data_id),
            business_area_id=str(rdi.business_area_id),
            program_id=str(rdi.program_id),
        )

    @mock.patch("hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
    @mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
    def test_not_start_importing_tasks(
        self,
        mock_get_all_celery_tasks: mock.MagicMock,
        mock_registration_xlsx_import_task_delay: mock.MagicMock,
    ) -> None:
        from hope.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        program = ProgramFactory()
        import_data = ImportData.objects.create()
        rdi = RegistrationDataImportFactory(
            name="IMPORTING",
            status=RegistrationDataImport.IMPORTING,
            data_source=RegistrationDataImport.XLS,
            program=program,
            import_data=import_data,
        )
        kwargs = {
            "registration_data_import_id": str(rdi.id),
            "import_data_id": str(rdi.import_data_id),
            "business_area_id": str(rdi.business_area_id),
            "program_id": str(rdi.program_id),
        }

        mock_get_all_celery_tasks.return_value = [
            {
                "name": "hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task",
                "kwargs": kwargs,
                "status": "active",
            }
        ]
        manager = RegistrationDataXlsxImportCeleryManager()
        manager.execute()
        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.IMPORTING
        assert mock_registration_xlsx_import_task_delay.call_count == 0

    @mock.patch("hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
    @mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
    def test_not_start_already_scheduled(
        self,
        mock_get_all_celery_tasks: mock.MagicMock,
        mock_registration_xlsx_import_task_delay: mock.MagicMock,
    ) -> None:
        from hope.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        program = ProgramFactory()
        import_data = ImportData.objects.create()
        rdi = RegistrationDataImportFactory(
            name="IMPORT_SCHEDULED",
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            data_source=RegistrationDataImport.XLS,
            program=program,
            import_data=import_data,
        )
        kwargs = {
            "registration_data_import_id": str(rdi.id),
            "import_data_id": str(rdi.import_data_id),
            "business_area_id": str(rdi.business_area_id),
            "program_id": str(rdi.program_id),
        }

        mock_get_all_celery_tasks.return_value = [
            {
                "name": "hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task",
                "kwargs": kwargs,
                "status": "queued",
            }
        ]
        manager = RegistrationDataXlsxImportCeleryManager()
        manager.execute()
        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
        assert mock_registration_xlsx_import_task_delay.call_count == 0

    @mock.patch("hope.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
    @mock.patch("hope.apps.utils.celery_manager.get_all_celery_tasks")
    def test_parametrized_by_business_area(
        self,
        mock_get_all_celery_tasks: mock.MagicMock,
        mock_registration_xlsx_import_task_delay: mock.MagicMock,
    ) -> None:
        from hope.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        program = ProgramFactory()
        import_data = ImportData.objects.create()
        rdi = RegistrationDataImportFactory(
            name="IMPORT_SCHEDULED afghanistan",
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            data_source=RegistrationDataImport.XLS,
            business_area=BusinessArea.objects.get(slug="afghanistan"),
            program=program,
            import_data=import_data,
        )

        import_data2 = ImportData.objects.create()
        RegistrationDataImportFactory(
            name="IMPORT_SCHEDULED sudan",
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            data_source=RegistrationDataImport.XLS,
            business_area=BusinessArea.objects.get(slug="sudan"),
            program=program,
            import_data=import_data2,
        )

        mock_get_all_celery_tasks.return_value = []
        manager = RegistrationDataXlsxImportCeleryManager(business_area=BusinessArea.objects.get(slug="afghanistan"))
        manager.execute()
        rdi.refresh_from_db()
        assert rdi.status == RegistrationDataImport.IMPORT_SCHEDULED
        assert mock_registration_xlsx_import_task_delay.call_count == 1
        mock_registration_xlsx_import_task_delay.assert_called_with(
            registration_data_import_id=str(rdi.id),
            import_data_id=str(rdi.import_data_id),
            business_area_id=str(rdi.business_area_id),
            program_id=str(rdi.program_id),
        )
