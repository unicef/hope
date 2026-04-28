from unittest.mock import Mock, patch

import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
from hope.apps.core.celery_tasks import async_job_task
from hope.apps.program.celery_tasks import (
    adjust_program_size_async_task,
    copy_program_async_task,
    populate_pdu_new_rounds_with_null_values_async_task,
)
from hope.models import AsyncJob, Program

pytestmark = pytest.mark.django_db


def queue_and_run_async_task(task: object, *args: object, **kwargs: object) -> object:
    with patch("hope.apps.program.celery_tasks.AsyncJob.queue", autospec=True):
        task(*args, **kwargs)
    job = AsyncJob.objects.latest("pk")
    return async_job_task.run(job._meta.label_lower, job.pk, job.version)


@patch("hope.apps.program.celery_tasks.program_copied.send")
@patch("hope.apps.program.celery_tasks.copy_program_related_data")
def test_copy_program_task_queues_and_runs_async_job(
    mock_copy_program_related_data: Mock, mock_program_copied: Mock
) -> None:
    program = ProgramFactory(business_area=BusinessAreaFactory())

    queue_and_run_async_task(copy_program_async_task, "source-program-id", str(program.id), "user-id")

    mock_copy_program_related_data.assert_called_once_with("source-program-id", program, "user-id")
    mock_program_copied.assert_called_once_with(sender=Program, instance=program)


@patch("hope.models.program.Program.adjust_program_size")
def test_adjust_program_size_task_queues_and_runs_async_job(mock_adjust_program_size: Mock) -> None:
    program = ProgramFactory(business_area=BusinessAreaFactory())

    queue_and_run_async_task(adjust_program_size_async_task, str(program.id))

    mock_adjust_program_size.assert_called_once_with()


@patch("hope.apps.program.celery_tasks.populate_pdu_new_rounds_with_null_values")
def test_populate_pdu_new_rounds_with_null_values_task_queues_and_runs_async_job(mock_populate: Mock) -> None:
    program = ProgramFactory(business_area=BusinessAreaFactory())

    queue_and_run_async_task(populate_pdu_new_rounds_with_null_values_async_task, str(program.id))

    mock_populate.assert_called_once_with(program)
