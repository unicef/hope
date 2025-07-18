from datetime import timedelta

from django.utils import timezone

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.contrib.aurora.models import Record


class TestClearRecordFilesTask(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.record_1 = Record.objects.create(
            registration=1,
            status=Record.STATUS_IMPORTED,
            timestamp=timezone.now() - timedelta(40),
            source_id=1,
            files=bytes("some_string1", "utf-8"),
        )

        cls.record_2 = Record.objects.create(
            registration=2,
            status=Record.STATUS_IMPORTED,
            timestamp=timezone.now() - timedelta(100),
            source_id=2,
            files=bytes("some_string_1", "utf-8"),
        )
        cls.record_3 = Record.objects.create(
            registration=3,
            status=Record.STATUS_ERROR,
            timestamp=timezone.now() - timedelta(99),
            source_id=3,
            files=bytes("some_string_12", "utf-8"),
        )
        cls.record_4 = Record.objects.create(
            registration=4,
            status=Record.STATUS_TO_IMPORT,
            timestamp=timezone.now() - timedelta(80),
            source_id=4,
            files=bytes("some_string_123", "utf-8"),
        )
        cls.record_5 = Record.objects.create(
            registration=5,
            status=Record.STATUS_IMPORTED,
            timestamp=timezone.now() - timedelta(75),
            source_id=5,
            files=bytes("some_string_1234", "utf-8"),
        )

    def test_clean_old_record_files_task(self) -> None:
        from hct_mis_api.contrib.aurora.celery_tasks import clean_old_record_files_task

        clean_old_record_files_task()
        assert Record.objects.count() == 3
