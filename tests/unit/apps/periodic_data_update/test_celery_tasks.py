from unittest.mock import patch

import pytest

from extras.test_utils.factories import PDUOnlineEditFactory, PDUXlsxTemplateFactory, PDUXlsxUploadFactory, UserFactory
from hope.apps.periodic_data_update.celery_tasks import (
    export_periodic_data_update_export_template_service_async_task,
    generate_pdu_online_edit_data_async_task,
    import_periodic_data_update_async_task,
    merge_pdu_online_edit_async_task,
    send_pdu_online_edit_notification_emails_async_task,
)
from hope.models import AsyncJob

pytestmark = pytest.mark.django_db


def test_import_periodic_data_update_queues_async_job() -> None:
    upload = PDUXlsxUploadFactory()

    with patch("hope.apps.periodic_data_update.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        import_periodic_data_update_async_task(upload)

    job = AsyncJob.objects.latest("pk")
    assert job.content_object == upload
    assert job.job_name == "import_periodic_data_update_async_task"
    assert job.program == upload.template.program
    assert job.action == "hope.apps.periodic_data_update.celery_tasks.import_periodic_data_update_async_task_action"
    assert job.config == {"periodic_data_update_upload_id": str(upload.id)}
    mock_queue.assert_called_once_with(job)


def test_export_periodic_data_update_export_template_service_queues_async_job() -> None:
    template = PDUXlsxTemplateFactory()

    with patch("hope.apps.periodic_data_update.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        export_periodic_data_update_export_template_service_async_task(template)

    job = AsyncJob.objects.latest("pk")
    assert job.content_object == template
    assert job.job_name == "export_periodic_data_update_export_template_service_async_task"
    assert job.program == template.program
    assert (
        job.action == "hope.apps.periodic_data_update.celery_tasks."
        "export_periodic_data_update_export_template_service_async_task_action"
    )
    assert job.config == {"periodic_data_update_template_id": str(template.id)}
    mock_queue.assert_called_once_with(job)


def test_generate_pdu_online_edit_data_task_queues_async_job() -> None:
    online_edit = PDUOnlineEditFactory()
    filters = {"field": "value"}
    rounds_data = [{"round": 1}]

    with patch("hope.apps.periodic_data_update.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        generate_pdu_online_edit_data_async_task(online_edit, filters, rounds_data)

    job = AsyncJob.objects.latest("pk")
    assert job.content_object == online_edit
    assert job.job_name == "generate_pdu_online_edit_data_async_task"
    assert job.program == online_edit.program
    assert job.action == "hope.apps.periodic_data_update.celery_tasks.generate_pdu_online_edit_data_async_task_action"
    assert job.config == {
        "pdu_online_edit_id": str(online_edit.id),
        "filters": filters,
        "rounds_data": rounds_data,
    }
    mock_queue.assert_called_once_with(job)


def test_merge_pdu_online_edit_task_queues_async_job() -> None:
    online_edit = PDUOnlineEditFactory()

    with patch("hope.apps.periodic_data_update.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        merge_pdu_online_edit_async_task(online_edit)

    job = AsyncJob.objects.latest("pk")
    assert job.content_object == online_edit
    assert job.job_name == "merge_pdu_online_edit_async_task"
    assert job.program == online_edit.program
    assert job.action == "hope.apps.periodic_data_update.celery_tasks.merge_pdu_online_edit_async_task_action"
    assert job.config == {"pdu_online_edit_id": str(online_edit.id)}
    mock_queue.assert_called_once_with(job)


def test_send_pdu_online_edit_notification_emails_queues_async_job() -> None:
    online_edit = PDUOnlineEditFactory()
    user = UserFactory()

    with patch("hope.apps.periodic_data_update.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        send_pdu_online_edit_notification_emails_async_task(online_edit, "approved", str(user.pk), "2026-03-20")

    job = AsyncJob.objects.latest("pk")
    assert job.content_object == online_edit
    assert job.job_name == "send_pdu_online_edit_notification_emails_async_task"
    assert job.program == online_edit.program
    assert (
        job.action
        == "hope.apps.periodic_data_update.celery_tasks.send_pdu_online_edit_notification_emails_async_task_action"
    )
    assert job.config == {
        "pdu_online_edit_id": str(online_edit.id),
        "action": "approved",
        "action_user_id": str(user.id),
        "action_date_formatted": "2026-03-20",
    }
    mock_queue.assert_called_once_with(job)
