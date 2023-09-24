from datetime import timedelta

from django.utils import timezone

from hct_mis_api.apps.core.base_test_case import APITestCase


class TestClearRecordFilesTask(APITestCase):
    databases = ["default", "registration_datahub"]

    @classmethod
    def setUpTestData(cls) -> None:
        from hct_mis_api.apps.registration_datahub.models import Record

        cls.record_1 = Record.objects.create(
            registration=1,
            status=Record.STATUS_IMPORTED,
            timestamp=timezone.now() - timedelta(40),
            source_id=1,
            files=b"1234567890",
        )

        cls.record_2 = Record.objects.create(
            registration=2,
            status=Record.STATUS_IMPORTED,
            timestamp=timezone.now() - timedelta(100),
            source_id=2,
            files=b"1234567890",
        )
        cls.record_3 = Record.objects.create(
            registration=3,
            status=Record.STATUS_ERROR,
            timestamp=timezone.now() - timedelta(99),
            source_id=3,
            files=b"1234567890",
        )
        cls.record_4 = Record.objects.create(
            registration=4,
            status=Record.STATUS_TO_IMPORT,
            timestamp=timezone.now() - timedelta(20),
            source_id=4,
            files=b"1234567890",
        )
        cls.record_5 = Record.objects.create(
            registration=5,
            status=Record.STATUS_IMPORTED,
            timestamp=timezone.now() - timedelta(75),
            source_id=5,
            files=b"1234567890",
        )

    def test_clean_old_record_files_task(self) -> None:
        from hct_mis_api.apps.registration_datahub.celery_tasks import (
            clean_old_record_files_task,
        )

        clean_old_record_files_task()

        self.record_1.refresh_from_db()
        self.record_2.refresh_from_db()
        self.record_3.refresh_from_db()
        self.record_4.refresh_from_db()
        self.record_5.refresh_from_db()

        print(self.record_1.files)
        print(len(self.record_1.files))
        self.assertEqual(self.record_1.files, b"1234567890")  # below 60 days
        self.assertIsNone(self.record_2.files)  # updated
        self.assertEqual(self.record_3.files, b"1234567890")  # status error
        self.assertEqual(self.record_4.files, b"1234567890")  # below 60 dats
        self.assertIsNone(self.record_5.files)  # updated
