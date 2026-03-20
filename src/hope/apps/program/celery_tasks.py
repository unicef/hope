from django_celery_boost.models import AsyncJobModel

from hope.apps.core.celery import app
from hope.apps.periodic_data_update.utils import (
    populate_pdu_new_rounds_with_null_values,
)
from hope.apps.program.signals import program_copied
from hope.apps.program.utils import copy_program_related_data
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag
from hope.models import AsyncJob, Program


def copy_program_task_action(job: AsyncJob) -> None:
    program = Program.objects.get(id=job.config["new_program_id"])
    set_sentry_business_area_tag(program.business_area.name)
    copy_program_related_data(job.config["copy_from_program_id"], program, job.config["user_id"])
    program_copied.send(sender=Program, instance=program)


@app.task()
@sentry_tags
@log_start_and_end
def copy_program_task(copy_from_program_id: str, new_program_id: str, user_id: str) -> None:
    job = AsyncJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.program.celery_tasks.copy_program_task_action",
        config={
            "copy_from_program_id": str(copy_from_program_id),
            "new_program_id": str(new_program_id),
            "user_id": str(user_id),
        },
        group_key=f"copy_program_task:{new_program_id}",
        description=f"Copy program {copy_from_program_id} to {new_program_id}",
    )
    job.queue()


def adjust_program_size_task_action(job: AsyncJob) -> bool:
    program = Program.objects.get(id=job.config["program_id"])
    set_sentry_business_area_tag(program.business_area.name)
    program.adjust_program_size()
    program.save(
        update_fields=(
            "household_count",
            "individual_count",
        )
    )
    return True


@app.task()
@sentry_tags
@log_start_and_end
def adjust_program_size_task(program_id: str) -> None:
    job = AsyncJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.program.celery_tasks.adjust_program_size_task_action",
        config={"program_id": str(program_id)},
        group_key=f"adjust_program_size_task:{program_id}",
        description=f"Adjust program size for {program_id}",
    )
    job.queue()


def populate_pdu_new_rounds_with_null_values_task_action(job: AsyncJob) -> bool:
    program = Program.objects.get(id=job.config["program_id"])
    set_sentry_business_area_tag(program.business_area.name)
    populate_pdu_new_rounds_with_null_values(program)
    return True


@app.task()
@sentry_tags
@log_start_and_end
def populate_pdu_new_rounds_with_null_values_task(program_id: str) -> None:
    job = AsyncJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.program.celery_tasks.populate_pdu_new_rounds_with_null_values_task_action",
        config={"program_id": str(program_id)},
        group_key=f"populate_pdu_new_rounds_with_null_values_task:{program_id}",
        description=f"Populate PDU rounds with null values for program {program_id}",
    )
    job.queue()
