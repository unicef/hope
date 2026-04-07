from hope.apps.periodic_data_update.utils import (
    populate_pdu_new_rounds_with_null_values,
)
from hope.apps.program.signals import program_copied
from hope.apps.program.utils import copy_program_related_data
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import AsyncJob, Program


def copy_program_task_action(job: AsyncJob) -> None:
    program = Program.objects.get(id=job.config["new_program_id"])
    set_sentry_business_area_tag(program.business_area.name)
    copy_program_related_data(job.config["copy_from_program_id"], program, job.config["user_id"])
    program_copied.send(sender=Program, instance=program)


def copy_program_task(copy_from_program_id: str, new_program_id: str, user_id: str) -> None:
    AsyncJob.queue_task(
        job_name=copy_program_task.__name__,
        program_id=new_program_id,
        action="hope.apps.program.celery_tasks.copy_program_task_action",
        config={
            "copy_from_program_id": copy_from_program_id,
            "new_program_id": new_program_id,
            "user_id": user_id,
        },
        group_key=f"copy_program_task:{new_program_id}",
        description=f"Copy program {copy_from_program_id} to {new_program_id}",
    )


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


def adjust_program_size_task(program_id: str) -> None:
    AsyncJob.queue_task(
        job_name=adjust_program_size_task.__name__,
        program_id=program_id,
        action="hope.apps.program.celery_tasks.adjust_program_size_task_action",
        config={"program_id": program_id},
        group_key=f"adjust_program_size_task:{program_id}",
        description=f"Adjust program size for {program_id}",
    )


def populate_pdu_new_rounds_with_null_values_task_action(job: AsyncJob) -> bool:
    program = Program.objects.get(id=job.config["program_id"])
    set_sentry_business_area_tag(program.business_area.name)
    populate_pdu_new_rounds_with_null_values(program)
    return True


def populate_pdu_new_rounds_with_null_values_task(program_id: str) -> None:
    AsyncJob.queue_task(
        job_name=populate_pdu_new_rounds_with_null_values_task.__name__,
        program_id=program_id,
        action="hope.apps.program.celery_tasks.populate_pdu_new_rounds_with_null_values_task_action",
        config={"program_id": program_id},
        group_key=f"populate_pdu_new_rounds_with_null_values_task:{program_id}",
        description=f"Populate PDU rounds with null values for program {program_id}",
    )
