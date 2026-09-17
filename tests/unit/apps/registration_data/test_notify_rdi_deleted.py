from unittest.mock import patch

import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.registration_data.api.country_workspace import CountryWorkspaceAPI
from hope.apps.registration_data.celery_tasks import (
    notify_rdi_deleted_async_task,
    notify_rdi_deleted_async_task_action,
    notify_rdi_deleted_on_failure,
)
from hope.models import AsyncRetryJob

pytestmark = pytest.mark.django_db

CALLBACK_URL = "https://cw.example.com/api/rdi/reset-callback/abc123"
SIGNED_TOKEN = "signed-token-abc123"
ACTION_PATH = "hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task_action"


def test_notify_enqueue_builds_config() -> None:
    program = ProgramFactory(business_area=BusinessAreaFactory(name="Afghanistan"))

    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue_task") as queue_task:
        notify_rdi_deleted_async_task(CALLBACK_URL, SIGNED_TOKEN, program)

    queue_task.assert_called_once()
    assert queue_task.call_args.kwargs["instance"] == program
    assert queue_task.call_args.kwargs["program"] == program
    config = queue_task.call_args.kwargs["config"]
    assert config["callback_url"] == CALLBACK_URL
    assert config["signed_token"] == SIGNED_TOKEN
    assert config["on_failure_action"] == "hope.apps.registration_data.celery_tasks.notify_rdi_deleted_on_failure"
    assert queue_task.call_args.kwargs["action"] == ACTION_PATH


def test_notify_action_calls_cw_api() -> None:
    job = AsyncRetryJob(config={"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN})

    with patch("hope.apps.registration_data.api.country_workspace.CountryWorkspaceAPI") as cw_api:
        notify_rdi_deleted_async_task_action(job)

    cw_api.assert_called_once_with(api_url=CALLBACK_URL)
    cw_api.return_value.notify_rdi_deleted.assert_called_once_with(SIGNED_TOKEN)


def test_notify_action_non_2xx_retries() -> None:
    job = AsyncRetryJob(config={"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN})

    with patch("hope.apps.registration_data.api.country_workspace.CountryWorkspaceAPI") as cw_api:
        cw_api.return_value.notify_rdi_deleted.side_effect = CountryWorkspaceAPI.CountryWorkspaceAPIError("502")
        with pytest.raises(CountryWorkspaceAPI.CountryWorkspaceAPIError):
            notify_rdi_deleted_async_task_action(job)


def test_notify_on_failure_hook_logs(caplog: pytest.LogCaptureFixture) -> None:
    job = AsyncRetryJob(pk=42, config={"callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN})

    with caplog.at_level("ERROR", logger="hope.apps.registration_data.celery_tasks"):
        notify_rdi_deleted_on_failure(job, RuntimeError("cw unreachable"))

    assert "never notified" in caplog.text
    assert CALLBACK_URL in caplog.text
    assert "cw unreachable" in caplog.text
