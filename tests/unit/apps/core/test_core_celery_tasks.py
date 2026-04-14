from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.utils import timezone
import pytest

from extras.test_utils.factories import XLSXKoboTemplateFactory
from hope.apps.core.celery_tasks import (
    upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task_action,
)
from hope.apps.core.tasks.upload_new_template_and_update_flex_fields import KoboRetriableError
from hope.models import AsyncRetryJob

pytestmark = pytest.mark.django_db


@pytest.fixture
def xlsx_kobo_template():
    return XLSXKoboTemplateFactory()


def test_upload_kobo_template_with_retry_raises_type_error_when_failed_time_is_none(xlsx_kobo_template):
    xlsx_kobo_template.first_connection_failed_time = None
    exc = KoboRetriableError(xlsx_kobo_template)

    mock_instance = MagicMock()
    mock_instance.execute.side_effect = exc
    mock_task_cls = MagicMock(return_value=mock_instance)

    with patch(
        "hope.apps.core.tasks.upload_new_template_and_update_flex_fields.UploadNewKoboTemplateAndUpdateFlexFieldsTask",
        mock_task_cls,
    ):
        job = AsyncRetryJob.objects.create(
            type="JOB_TASK",
            action="hope.apps.core.celery_tasks.upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task_action",
            config={"xlsx_kobo_template_id": str(xlsx_kobo_template.id)},
        )
        with pytest.raises(TypeError):
            upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task_action(job)


def test_upload_kobo_template_with_retry_sets_unsuccessful_when_failed_time_is_old(xlsx_kobo_template):
    from hope.models import XLSXKoboTemplate

    xlsx_kobo_template.first_connection_failed_time = timezone.now() - timedelta(days=2)
    xlsx_kobo_template.save()
    exc = KoboRetriableError(xlsx_kobo_template)

    mock_instance = MagicMock()
    mock_instance.execute.side_effect = exc
    mock_task_cls = MagicMock(return_value=mock_instance)

    with patch(
        "hope.apps.core.tasks.upload_new_template_and_update_flex_fields.UploadNewKoboTemplateAndUpdateFlexFieldsTask",
        mock_task_cls,
    ):
        job = AsyncRetryJob.objects.create(
            type="JOB_TASK",
            action="hope.apps.core.celery_tasks.upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task_action",
            config={"xlsx_kobo_template_id": str(xlsx_kobo_template.id)},
        )
        upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task_action(job)

    assert exc.xlsx_kobo_template_object.status == XLSXKoboTemplate.UNSUCCESSFUL


def test_upload_kobo_template_with_retry_retries_when_failed_time_is_recent(xlsx_kobo_template):
    xlsx_kobo_template.first_connection_failed_time = timezone.now() - timedelta(minutes=30)
    exc = KoboRetriableError(xlsx_kobo_template)

    mock_instance = MagicMock()
    mock_instance.execute.side_effect = exc
    mock_task_cls = MagicMock(return_value=mock_instance)

    with (
        patch(
            "hope.apps.core.tasks.upload_new_template_and_update_flex_fields.UploadNewKoboTemplateAndUpdateFlexFieldsTask",
            mock_task_cls,
        ),
        patch(
            "hope.apps.core.celery_tasks.upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task"
        ) as mock_retry_task,
    ):
        job = AsyncRetryJob.objects.create(
            type="JOB_TASK",
            action="hope.apps.core.celery_tasks.upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task_action",
            config={"xlsx_kobo_template_id": str(xlsx_kobo_template.id)},
        )
        upload_new_kobo_template_and_update_flex_fields_task_with_retry_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"exception": str(exc)}
    mock_retry_task.assert_called_once_with(str(xlsx_kobo_template.id))
