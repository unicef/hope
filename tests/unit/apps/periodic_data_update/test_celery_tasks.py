from unittest.mock import patch

import pytest

from extras.test_utils.factories import PDUOnlineEditFactory, PDUXlsxTemplateFactory, PDUXlsxUploadFactory, UserFactory
from hope.apps.periodic_data_update.celery_tasks import (
    export_periodic_data_update_export_template_service,
    generate_pdu_online_edit_data_task,
    import_periodic_data_update,
    merge_pdu_online_edit_task,
    send_pdu_online_edit_notification_emails,
)
from hope.models import AsyncJob

pytestmark = pytest.mark.django_db


def test_import_periodic_data_update_queues_async_job() -> None:
    upload = PDUXlsxUploadFactory()

    with patch("hope.apps.periodic_data_update.celery_tasks.AsyncJob.queue", autospec=True) as mock_queue:
        import_periodic_data_update.delay(str(upload.id))

    job = AsyncJob.objects.latest("pk")
    assert job.content_object == upload
    assert job.job_name == "import_periodic_data_update"
    assert job.program == upload.template.program
    assert job.action == "hope.apps.periodic_data_update.celery_tasks.import_periodic_data_update_action"
    assert job.config == {"periodic_data_update_upload_id": str(upload.id)}
    mock_queue.assert_called_once_with(job)


def test_export_periodic_data_update_export_template_service_queues_async_job() -> None:
    template = PDUXlsxTemplateFactory()

    with patch("hope.apps.periodic_data_update.celery_tasks.AsyncJob.queue", autospec=True) as mock_queue:
        export_periodic_data_update_export_template_service.delay(str(template.id))

    job = AsyncJob.objects.latest("pk")
    assert job.content_object == template
    assert job.job_name == "export_periodic_data_update_export_template_service"
    assert job.program == template.program
    assert (
        job.action
        == "hope.apps.periodic_data_update.celery_tasks.export_periodic_data_update_export_template_service_action"
    )
    assert job.config == {"periodic_data_update_template_id": str(template.id)}
    mock_queue.assert_called_once_with(job)


def test_generate_pdu_online_edit_data_task_queues_async_job() -> None:
    online_edit = PDUOnlineEditFactory()
    filters = {"field": "value"}
    rounds_data = [{"round": 1}]

    with patch("hope.apps.periodic_data_update.celery_tasks.AsyncJob.queue", autospec=True) as mock_queue:
        generate_pdu_online_edit_data_task.delay(online_edit.id, filters, rounds_data)

    job = AsyncJob.objects.latest("pk")
    assert job.content_object == online_edit
    assert job.job_name == "generate_pdu_online_edit_data_task"
    assert job.program == online_edit.program
    assert job.action == "hope.apps.periodic_data_update.celery_tasks.generate_pdu_online_edit_data_task_action"
    assert job.config == {
        "pdu_online_edit_id": online_edit.id,
        "filters": filters,
        "rounds_data": rounds_data,
    }
    mock_queue.assert_called_once_with(job)


def test_merge_pdu_online_edit_task_queues_async_job() -> None:
    online_edit = PDUOnlineEditFactory()

    with patch("hope.apps.periodic_data_update.celery_tasks.AsyncJob.queue", autospec=True) as mock_queue:
        merge_pdu_online_edit_task.delay(online_edit.id)

    job = AsyncJob.objects.latest("pk")
    assert job.content_object == online_edit
    assert job.job_name == "merge_pdu_online_edit_task"
    assert job.program == online_edit.program
    assert job.action == "hope.apps.periodic_data_update.celery_tasks.merge_pdu_online_edit_task_action"
    assert job.config == {"pdu_online_edit_id": online_edit.id}
    mock_queue.assert_called_once_with(job)


def test_send_pdu_online_edit_notification_emails_queues_async_job() -> None:
    online_edit = PDUOnlineEditFactory()
    user = UserFactory()

    with patch("hope.apps.periodic_data_update.celery_tasks.AsyncJob.queue", autospec=True) as mock_queue:
        send_pdu_online_edit_notification_emails.delay(online_edit.id, "approved", str(user.id), "2026-03-20")

    job = AsyncJob.objects.latest("pk")
    assert job.content_object == online_edit
    assert job.job_name == "send_pdu_online_edit_notification_emails"
    assert job.program == online_edit.program
    assert job.action == "hope.apps.periodic_data_update.celery_tasks.send_pdu_online_edit_notification_emails_action"
    assert job.config == {
        "pdu_online_edit_id": online_edit.id,
        "action": "approved",
        "action_user_id": str(user.id),
        "action_date_formatted": "2026-03-20",
    }
    mock_queue.assert_called_once_with(job)
