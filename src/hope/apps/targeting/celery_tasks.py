import logging

from celery.exceptions import TaskError
from django.db.transaction import atomic
from django.utils import timezone

from hope.apps.core.celery import app
from hope.apps.household.forms import CreateTargetPopulationTextForm
from hope.models import PaymentPlan
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models.program import Program
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)


@app.task()
@log_start_and_end
@sentry_tags
def create_tp_from_list(form_data: dict[str, str], user_id: str, program_pk: str) -> None:
    program = Program.objects.get(pk=program_pk)
    form = CreateTargetPopulationTextForm(form_data, program=program)
    if form.is_valid():
        set_sentry_business_area_tag(program.business_area.name)
        program_cycle = form.cleaned_data["program_cycle"]
        try:
            with atomic():
                payment_plan = PaymentPlan.objects.create(
                    created_by_id=user_id,
                    name=form.cleaned_data["name"],
                    business_area=program_cycle.program.business_area,
                    program_cycle=program_cycle,
                    status_date=timezone.now(),
                    start_date=program_cycle.start_date,
                    end_date=program_cycle.end_date,
                    status=PaymentPlan.Status.TP_OPEN,
                    build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
                    built_at=timezone.now(),
                )
                # update statistics and create payments
                payment_plan.build_status_building()
                payment_plan.save(update_fields=("build_status", "built_at"))
                PaymentPlanService.create_payments(payment_plan)
                payment_plan.update_population_count_fields()
                payment_plan.build_status_ok()
                payment_plan.save(update_fields=("build_status", "built_at"))
        except Exception as e:
            logger.exception(e)
    else:
        error_message = f"Form validation failed: {form.errors}."
        logger.warning(error_message)
        raise TaskError(error_message)
