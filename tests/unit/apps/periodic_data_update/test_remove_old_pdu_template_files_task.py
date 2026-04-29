"""Tests for remove old PDU template files task."""

from datetime import timedelta
from tempfile import NamedTemporaryFile
from typing import Any
from unittest.mock import patch

from django.contrib.admin.options import get_content_type_for_model
from django.core.files.base import ContentFile
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PDUXlsxTemplateFactory,
)
from hope.apps.core.celery_tasks import async_retry_job_task
from hope.apps.periodic_data_update.celery_tasks import (
    remove_old_pdu_template_files_async_task,
    remove_old_pdu_template_files_async_task_action,
)
from hope.models import AsyncRetryJob, BusinessArea, FileTemp, PDUXlsxTemplate, PeriodicAsyncRetryJob

pytestmark = pytest.mark.django_db


def queue_and_run_retry_task(task: object, *args: object, **kwargs: object) -> object:
    with patch("hope.apps.periodic_data_update.celery_tasks.PeriodicAsyncRetryJob.queue", autospec=True):
        task.delay(*args, **kwargs)
    job = PeriodicAsyncRetryJob.objects.latest("pk")
    return async_retry_job_task.run(job._meta.label_lower, job.pk, job.version)


def create_file_for_template(pdu_template: PDUXlsxTemplate, days_ago: int) -> None:
    filename = f"Test File {pdu_template.pk}.xlsx"
    file_content = b"Test content"
    with NamedTemporaryFile(delete=False) as file_temp:
        file_temp.write(file_content)
        file_temp.flush()

    creation_time = timezone.now() - timedelta(days=days_ago)
    file = FileTemp.objects.create(
        object_id=pdu_template.pk,
        content_type=get_content_type_for_model(pdu_template),
        created=creation_time,
        file=ContentFile(file_content, filename),
    )
    pdu_template.file = file
    pdu_template.status = PDUXlsxTemplate.Status.EXPORTED
    pdu_template.save()


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def pdu_template1(business_area: BusinessArea) -> PDUXlsxTemplate:
    template = PDUXlsxTemplateFactory()
    template.refresh_from_db()
    create_file_for_template(template, days_ago=10)  # Recent file
    return template


@pytest.fixture
def pdu_template2(business_area: BusinessArea) -> PDUXlsxTemplate:
    template = PDUXlsxTemplateFactory()
    create_file_for_template(template, days_ago=35)  # Old file
    return template


@pytest.fixture
def pdu_template3(business_area: BusinessArea) -> PDUXlsxTemplate:
    template = PDUXlsxTemplateFactory()
    create_file_for_template(template, days_ago=40)  # Older file
    return template


def test_remove_old_pdu_template_files_task(
    pdu_template1: PDUXlsxTemplate,
    pdu_template2: PDUXlsxTemplate,
    pdu_template3: PDUXlsxTemplate,
) -> None:
    # Verify initial state
    assert pdu_template1.file is not None  # Not older than 30 days
    assert pdu_template2.file is not None  # Older than 30 days
    assert pdu_template3.file is not None  # Older than 30 days

    assert pdu_template1.status == PDUXlsxTemplate.Status.EXPORTED
    assert pdu_template2.status == PDUXlsxTemplate.Status.EXPORTED
    assert pdu_template3.status == PDUXlsxTemplate.Status.EXPORTED

    # Run the task
    queue_and_run_retry_task(remove_old_pdu_template_files_async_task)

    pdu_template1.refresh_from_db()
    pdu_template2.refresh_from_db()
    pdu_template3.refresh_from_db()

    # Verify files older than 30 days were removed
    assert pdu_template1.file is not None  # Not older than 30 days
    assert pdu_template2.file is None  # Older than 30 days
    assert pdu_template3.file is None  # Older than 30 days

    assert pdu_template1.status == PDUXlsxTemplate.Status.EXPORTED
    assert pdu_template2.status == PDUXlsxTemplate.Status.TO_EXPORT
    assert pdu_template3.status == PDUXlsxTemplate.Status.TO_EXPORT

    assert pdu_template1.can_export is False
    assert pdu_template2.can_export is True
    assert pdu_template3.can_export is True


def test_remove_old_pdu_template_files_task_increments_template_version_cache_for_updated_templates(
    pdu_template2: PDUXlsxTemplate,
    pdu_template3: PDUXlsxTemplate,
) -> None:
    with patch(
        "hope.apps.periodic_data_update.celery_tasks.increment_periodic_data_update_template_version_cache_function"
    ) as mock_increment:
        queue_and_run_retry_task(remove_old_pdu_template_files_async_task)

    assert mock_increment.call_count == 2
    mock_increment.assert_any_call(pdu_template2.business_area.slug, pdu_template2.program_id)
    mock_increment.assert_any_call(pdu_template3.business_area.slug, pdu_template3.program_id)


def test_remove_old_pdu_template_files_task_action_returns_without_old_files() -> None:
    job = AsyncRetryJob(config={"expiration_days": 30})

    with patch(
        "hope.apps.periodic_data_update.celery_tasks.increment_periodic_data_update_template_version_cache_function"
    ) as mock_increment:
        result = remove_old_pdu_template_files_async_task_action(job)

    assert result is None
    assert FileTemp.objects.count() == 0
    mock_increment.assert_not_called()
