from datetime import timedelta
from typing import TYPE_CHECKING

from django.utils import timezone
import pytest

from extras.test_utils.factories import RecordFactory
from hope.contrib.aurora.celery_tasks import clean_old_record_files_task
from hope.contrib.aurora.models import Record

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

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


def test_clean_old_record_files_task_empty() -> None:
    # No records at all
    clean_old_record_files_task()
    assert Record.objects.count() == 0


def test_clean_old_record_files_task_batching(mocker: "MockerFixture") -> None:
    now = timezone.now()
    # Create 5 records that should be deleted
    RecordFactory.create_batch(5, status=Record.STATUS_IMPORTED, timestamp=now - timedelta(days=100))

    # Run with batch_size=2, should take 3 batches (2+2+1)
    clean_old_record_files_task(batch_size=2)

    assert Record.objects.count() == 0


def test_clean_old_record_files_task_logging(mocker: "MockerFixture") -> None:
    now = timezone.now()
    RecordFactory.create_batch(3, status=Record.STATUS_IMPORTED, timestamp=now - timedelta(days=100))
    mock_logger = mocker.patch("hope.contrib.aurora.celery_tasks.logger")

    clean_old_record_files_task(batch_size=2)

    # Should log 2 batches and one final message
    assert mock_logger.info.call_count == 3
    mock_logger.info.assert_any_call("Batch 1/2 (2 deleted, total: 2/3)")
    mock_logger.info.assert_any_call("Batch 2/2 (1 deleted, total: 3/3)")
    mock_logger.info.assert_any_call("Record files have been successfully cleared")


def test_clean_old_record_files_task_error_handling(mocker: "MockerFixture") -> None:
    mock_logger = mocker.patch("hope.contrib.aurora.celery_tasks.logger")
    # Force an exception by mocking timezone.now to raise something
    mocker.patch("hope.contrib.aurora.celery_tasks.timezone.now", side_effect=Exception("Database error"))

    with pytest.raises(Exception, match="Database error"):
        clean_old_record_files_task()

    mock_logger.exception.assert_called_once_with("Error cleaning old record files")
