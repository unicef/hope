from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.utils import timezone
import pytest

from extras.test_utils.factories import XLSXKoboTemplateFactory
from hope.apps.core.celery_tasks import upload_new_kobo_template_and_update_flex_fields_task_with_retry
from hope.apps.core.tasks.upload_new_template_and_update_flex_fields import KoboRetriableError
from hope.models import XLSXKoboTemplate

pytestmark = pytest.mark.django_db


@pytest.fixture
def xlsx_kobo_template():
    return XLSXKoboTemplateFactory()


def test_upload_kobo_template_with_retry_sets_unsuccessful_when_failed_time_is_none(xlsx_kobo_template):
    xlsx_kobo_template.first_connection_failed_time = None
    exc = KoboRetriableError(xlsx_kobo_template)

    mock_instance = MagicMock()
    mock_instance.execute.side_effect = exc
    mock_task_cls = MagicMock(return_value=mock_instance)

    with patch(
        "hope.apps.core.tasks.upload_new_template_and_update_flex_fields.UploadNewKoboTemplateAndUpdateFlexFieldsTask",
        mock_task_cls,
    ):
        upload_new_kobo_template_and_update_flex_fields_task_with_retry.run(
            xlsx_kobo_template_id=str(xlsx_kobo_template.id)
        )

    assert xlsx_kobo_template.status == XLSXKoboTemplate.UNSUCCESSFUL


def test_upload_kobo_template_with_retry_retries_when_failed_time_is_recent(xlsx_kobo_template):
    # With CELERY_TASK_ALWAYS_EAGER=True, self.retry() re-runs the task eagerly.
    # After max_retries are exhausted, the original exc (KoboRetriableError) is re-raised.
    xlsx_kobo_template.first_connection_failed_time = timezone.now() - timedelta(minutes=30)
    exc = KoboRetriableError(xlsx_kobo_template)

    mock_instance = MagicMock()
    mock_instance.execute.side_effect = exc
    mock_task_cls = MagicMock(return_value=mock_instance)

    with patch(
        "hope.apps.core.tasks.upload_new_template_and_update_flex_fields.UploadNewKoboTemplateAndUpdateFlexFieldsTask",
        mock_task_cls,
    ):
        with pytest.raises(KoboRetriableError):
            upload_new_kobo_template_and_update_flex_fields_task_with_retry.run(
                xlsx_kobo_template_id=str(xlsx_kobo_template.id)
            )
