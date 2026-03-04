from datetime import timedelta

from django.utils import timezone
import pytest

from extras.test_utils.factories import RecordFactory
from hope.contrib.aurora.celery_tasks import clean_old_record_files_task
from hope.contrib.aurora.models import Record

pytestmark = pytest.mark.django_db


@pytest.fixture
def record_set() -> dict[str, Record]:
    now = timezone.now()
    return {
        "recent_imported": RecordFactory(
            status=Record.STATUS_IMPORTED,
            timestamp=now - timedelta(days=40),
            files=b"some_string1",
        ),
        "old_imported": RecordFactory(
            status=Record.STATUS_IMPORTED,
            timestamp=now - timedelta(days=100),
            files=b"some_string_1",
        ),
        "old_error": RecordFactory(
            status=Record.STATUS_ERROR,
            timestamp=now - timedelta(days=99),
            files=b"some_string_12",
        ),
        "old_to_import": RecordFactory(
            status=Record.STATUS_TO_IMPORT,
            timestamp=now - timedelta(days=80),
            files=b"some_string_123",
        ),
        "old_imported_remove": RecordFactory(
            status=Record.STATUS_IMPORTED,
            timestamp=now - timedelta(days=75),
            files=b"some_string_1234",
        ),
    }


def test_clean_old_record_files_task(record_set: dict[str, Record]) -> None:
    clean_old_record_files_task()

    assert Record.objects.count() == 3
    remaining_ids = set(Record.objects.values_list("id", flat=True))
    assert record_set["recent_imported"].id in remaining_ids
    assert record_set["old_error"].id in remaining_ids
    assert record_set["old_to_import"].id in remaining_ids
