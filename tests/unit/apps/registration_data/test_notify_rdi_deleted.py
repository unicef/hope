from unittest.mock import patch

import pytest

from hope.apps.registration_data.api.country_workspace import CountryWorkspaceAPI
from hope.apps.registration_data.celery_tasks import (
    notify_rdi_deleted_async_task,
    notify_rdi_deleted_async_task_action,
)
from hope.models import AsyncRetryJob

CALLBACK_URL = "https://cw.example.com/api/rdi/reset-callback/abc123"
SIGNED_TOKEN = "signed-token-abc123"

ACTION_PATH = "hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task_action"
CW_API_PATH = "hope.apps.registration_data.api.country_workspace.CountryWorkspaceAPI"


def test_notify_enqueue_builds_config() -> None:
    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue_task") as queue_task:
        notify_rdi_deleted_async_task(CALLBACK_URL, SIGNED_TOKEN)

    queue_task.assert_called_once()
    assert queue_task.call_args.kwargs["config"] == {"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN}
    assert queue_task.call_args.kwargs["action"] == ACTION_PATH


def test_notify_action_calls_cw_api() -> None:
    job = AsyncRetryJob(config={"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN})

    with patch(CW_API_PATH) as cw_api:
        notify_rdi_deleted_async_task_action(job)

    cw_api.assert_called_once_with(api_url=CALLBACK_URL)
    cw_api.return_value.notify_rdi_deleted.assert_called_once_with(SIGNED_TOKEN)


def test_notify_action_non_2xx_retries() -> None:
    job = AsyncRetryJob(config={"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN})

    with patch(CW_API_PATH) as cw_api:
        cw_api.return_value.notify_rdi_deleted.side_effect = CountryWorkspaceAPI.CountryWorkspaceAPIError("502")
        with pytest.raises(CountryWorkspaceAPI.CountryWorkspaceAPIError):
            notify_rdi_deleted_async_task_action(job)
