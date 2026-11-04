import logging
from uuid import UUID

from celery.exceptions import TaskError
from django.db.transaction import atomic
from django.utils import timezone

from hope.apps.household.forms import CreateTargetPopulationTextForm
from hope.apps.payment.flows import PaymentListFlow
from hope.apps.payment.services.payment_list_services import PaymentListService
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import AsyncJob, PaymentList, Program

logger = logging.getLogger(__name__)


def _serialize_form_data(value: object) -> object:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {key: _serialize_form_data(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize_form_data(item) for item in value]
    return value


def create_tp_from_list_async_task_action(job: AsyncJob) -> None:
    program = Program.objects.get(pk=job.config["program_pk"])
    form = CreateTargetPopulationTextForm(job.config["form_data"], program=program)
    if form.is_valid():
        set_sentry_business_area_tag(program.business_area.name)
        program_cycle = form.cleaned_data["program_cycle"]
        with atomic():
            payment_list = PaymentList.objects.create(
                created_by_id=job.config["user_id"],
                name=form.cleaned_data["name"],
                business_area=program_cycle.program.business_area,
                program_cycle=program_cycle,
                payment_plan=form.cleaned_data["payment_plan"],
                status_date=timezone.now(),
                start_date=program_cycle.start_date,
                end_date=program_cycle.end_date,
                status=PaymentList.Status.TP_OPEN,
                build_status=PaymentList.BuildStatus.BUILD_STATUS_PENDING,
                built_at=timezone.now(),
            )
            payment_list.payment_plan_purposes.set(program.payment_plan_purposes.all())
            flow = PaymentListFlow(payment_list)
            flow.build_status_building()
            payment_list.save(update_fields=("build_status", "built_at"))
            PaymentListService.create_payments(payment_list)
            payment_list.update_population_count_fields()
            flow = PaymentListFlow(payment_list)
            flow.build_status_ok()
            payment_list.save(update_fields=("build_status", "built_at"))

    else:
        error_message = f"Form validation failed: {form.errors}."
        logger.warning(error_message)
        raise TaskError(error_message)


def create_tp_from_list_async_task(form_data: dict[str, str], user_id: str, program_pk: str) -> None:
    config = {
        "form_data": _serialize_form_data(form_data),
        "user_id": user_id,
        "program_pk": program_pk,
    }
    AsyncJob.queue_task(
        job_name=create_tp_from_list_async_task.__name__,
        program_id=program_pk,
        action="hope.apps.targeting.celery_tasks.create_tp_from_list_async_task_action",
        config=config,
        group_key="targeting",
        description=f"Create target population from list for program {program_pk}",
    )
