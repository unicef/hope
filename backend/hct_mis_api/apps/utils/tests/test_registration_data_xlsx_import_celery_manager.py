from unittest import mock

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    ImportData,
    RegistrationDataImportDatahub,
)


class TestRegistrationDataXlsxImportCeleryManager(APITestCase):
    databases = {"default", "registration_datahub"}

    @classmethod
    def setUpTestData(cls) -> None:
        pass

    @mock.patch("hct_mis_api.apps.utils.celery_manager.get_all_celery_tasks")
    def test_querysets(self, _: mock.MagicMock) -> None:
        from hct_mis_api.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        manager = RegistrationDataXlsxImportCeleryManager()
        rdi_import_scheduled = RegistrationDataImportFactory(
            name="IMPORT_SCHEDULED",
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            data_source=RegistrationDataImport.XLS,
        )
        rdi_importing = RegistrationDataImportFactory(
            name="IMPORTING", status=RegistrationDataImport.IMPORTING, data_source=RegistrationDataImport.XLS
        )
        RegistrationDataImportFactory(
            name="IMPORT_ERROR", status=RegistrationDataImport.IMPORT_ERROR, data_source=RegistrationDataImport.XLS
        )
        RegistrationDataImportFactory(
            name="REFUSED_IMPORT", status=RegistrationDataImport.REFUSED_IMPORT, data_source=RegistrationDataImport.XLS
        )
        RegistrationDataImportFactory(
            name="DEDUPLICATION", status=RegistrationDataImport.DEDUPLICATION, data_source=RegistrationDataImport.XLS
        )
        RegistrationDataImportFactory(
            name="DEDUPLICATION_FAILED",
            status=RegistrationDataImport.DEDUPLICATION_FAILED,
            data_source=RegistrationDataImport.XLS,
        )
        RegistrationDataImportFactory(
            name="MERGE_SCHEDULED",
            status=RegistrationDataImport.MERGE_SCHEDULED,
            data_source=RegistrationDataImport.XLS,
        )
        RegistrationDataImportFactory(
            name="MERGING", status=RegistrationDataImport.MERGING, data_source=RegistrationDataImport.XLS
        )
        RegistrationDataImportFactory(
            name="MERGE_ERROR", status=RegistrationDataImport.MERGE_ERROR, data_source=RegistrationDataImport.XLS
        )
        RegistrationDataImportFactory(
            name="MERGED", status=RegistrationDataImport.MERGED, data_source=RegistrationDataImport.XLS
        )
        self.assertEqual(manager.pending_queryset.count(), 1)
        self.assertEqual(manager.pending_queryset.first(), rdi_import_scheduled)
        self.assertEqual(manager.in_progress_queryset.count(), 1)
        self.assertEqual(manager.in_progress_queryset.first(), rdi_importing)

    @mock.patch("hct_mis_api.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
    @mock.patch("hct_mis_api.apps.utils.celery_manager.get_all_celery_tasks")
    def test_add_scheduled_to_queue(
        self,
        mock_get_all_celery_tasks: mock.MagicMock,
        mock_registration_xlsx_import_task_delay: mock.MagicMock,
    ) -> None:
        from hct_mis_api.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        mock_get_all_celery_tasks.return_value = []
        rdi = RegistrationDataImportFactory(
            name="IMPORT_SCHEDULED",
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            data_source=RegistrationDataImport.XLS,
        )
        import_data = ImportData.objects.create()
        rdi_datahub = RegistrationDataImportDatahub.objects.create(hct_id=rdi.id, import_data=import_data)
        rdi.datahub_id = rdi_datahub.id
        manager = RegistrationDataXlsxImportCeleryManager()
        manager.execute()
        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.IMPORT_SCHEDULED)
        self.assertEqual(mock_registration_xlsx_import_task_delay.call_count, 1)
        mock_registration_xlsx_import_task_delay.assert_called_with(
            **{
                "registration_data_import_id": str(rdi_datahub.id),
                "import_data_id": str(rdi_datahub.import_data_id),
                "business_area_id": str(rdi.business_area_id),
            }
        )

    @mock.patch("hct_mis_api.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
    @mock.patch("hct_mis_api.apps.utils.celery_manager.get_all_celery_tasks")
    def test_revert_status_rdi_with_importing_status(
        self,
        mock_get_all_celery_tasks: mock.MagicMock,
        mock_registration_xlsx_import_task_delay: mock.MagicMock,
    ) -> None:
        from hct_mis_api.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        mock_get_all_celery_tasks.return_value = []
        rdi = RegistrationDataImportFactory(
            name="IMPORTING",
            status=RegistrationDataImport.IMPORTING,
            data_source=RegistrationDataImport.XLS,
        )
        import_data = ImportData.objects.create()
        rdi_datahub = RegistrationDataImportDatahub.objects.create(hct_id=rdi.id, import_data=import_data)
        rdi.datahub_id = rdi_datahub.id
        manager = RegistrationDataXlsxImportCeleryManager()
        manager.execute()
        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.IMPORT_SCHEDULED)
        self.assertEqual(mock_registration_xlsx_import_task_delay.call_count, 1)
        mock_registration_xlsx_import_task_delay.assert_called_with(
            **{
                "registration_data_import_id": str(rdi_datahub.id),
                "import_data_id": str(rdi_datahub.import_data_id),
                "business_area_id": str(rdi.business_area_id),
            }
        )

    @mock.patch("hct_mis_api.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
    @mock.patch("hct_mis_api.apps.utils.celery_manager.get_all_celery_tasks")
    def test_not_start_importing_tasks(
        self,
        mock_get_all_celery_tasks: mock.MagicMock,
        mock_registration_xlsx_import_task_delay: mock.MagicMock,
    ) -> None:
        from hct_mis_api.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        rdi = RegistrationDataImportFactory(
            name="IMPORTING",
            status=RegistrationDataImport.IMPORTING,
            data_source=RegistrationDataImport.XLS,
        )
        import_data = ImportData.objects.create()
        rdi_datahub = RegistrationDataImportDatahub.objects.create(hct_id=rdi.id, import_data=import_data)
        rdi.datahub_id = rdi_datahub.id
        kwargs = {
            "registration_data_import_id": str(rdi_datahub.id),
            "import_data_id": str(rdi_datahub.import_data_id),
            "business_area_id": str(rdi.business_area_id),
        }

        mock_get_all_celery_tasks.return_value = [
            {
                "name": "hct_mis_api.apps.registration_datahub.celery_tasks.registration_xlsx_import_task",
                "kwargs": kwargs,
                "status": "active",
            }
        ]
        manager = RegistrationDataXlsxImportCeleryManager()
        manager.execute()
        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.IMPORTING)
        self.assertEqual(mock_registration_xlsx_import_task_delay.call_count, 0)

    @mock.patch("hct_mis_api.apps.registration_datahub.celery_tasks.registration_xlsx_import_task.delay")
    @mock.patch("hct_mis_api.apps.utils.celery_manager.get_all_celery_tasks")
    def test_not_start_already_scheduled(
        self,
        mock_get_all_celery_tasks: mock.MagicMock,
        mock_registration_xlsx_import_task_delay: mock.MagicMock,
    ) -> None:
        from hct_mis_api.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        rdi = RegistrationDataImportFactory(
            name="IMPORT_SCHEDULED",
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            data_source=RegistrationDataImport.XLS,
        )
        import_data = ImportData.objects.create()
        rdi_datahub = RegistrationDataImportDatahub.objects.create(hct_id=rdi.id, import_data=import_data)
        rdi.datahub_id = rdi_datahub.id
        kwargs = {
            "registration_data_import_id": str(rdi_datahub.id),
            "import_data_id": str(rdi_datahub.import_data_id),
            "business_area_id": str(rdi.business_area_id),
        }

        mock_get_all_celery_tasks.return_value = [
            {
                "name": "hct_mis_api.apps.registration_datahub.celery_tasks.registration_xlsx_import_task",
                "kwargs": kwargs,
                "status": "queued",
            }
        ]
        manager = RegistrationDataXlsxImportCeleryManager()
        manager.execute()
        rdi.refresh_from_db()
        self.assertEqual(rdi.status, RegistrationDataImport.IMPORT_SCHEDULED)
        self.assertEqual(mock_registration_xlsx_import_task_delay.call_count, 0)
