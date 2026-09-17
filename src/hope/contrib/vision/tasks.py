from django.db import transaction
from django.utils import timezone

from hope.contrib.vision.api import VisionAPI, VisionAPIError, VisionAPIMissingCredentialsError
from hope.contrib.vision.choices import VISION_SEND_MUTABLE_STATUSES, VisionLogEntryType, VisionStatus
from hope.contrib.vision.services import VisionService
from hope.models import AsyncJob, PaymentPlan


def send_payment_plan_to_vision_async_task_action(job: AsyncJob) -> None:
    with transaction.atomic():
        payment_plan = (
            PaymentPlan.objects.select_for_update()
            .select_related("business_area")
            .get(pk=job.config["payment_plan_id"])
        )
        if not payment_plan.can_send_to_vision:
            return

        # Lock and recheck immediately before marking the request in flight. This prevents an older task instance
        # from restoring the Vision attempt after an abort or rejection has reset it.
        VisionService.set_status(payment_plan, VisionStatus.WAITING_FOR_CALLBACK)
        payment_plan.save(update_fields=["internal_data"])

    try:
        VisionAPI().send_payment_plan(payment_plan)
    except (VisionAPIError, VisionAPIMissingCredentialsError) as error:
        with transaction.atomic():
            locked_payment_plan = PaymentPlan.objects.select_for_update().get(pk=payment_plan.pk)
            if (
                locked_payment_plan.status == PaymentPlan.Status.IN_REVIEW
                and locked_payment_plan.vision_status in VISION_SEND_MUTABLE_STATUSES
            ):
                if locked_payment_plan.vision_status != VisionStatus.SEND_FAILED.value:
                    VisionService.vision_data(locked_payment_plan).setdefault("log", []).append(
                        {
                            "timestamp": timezone.now().isoformat(),
                            "type": VisionLogEntryType.API_CALL.value,
                            "payload": {},
                            "response": {"error": type(error).__name__},
                        }
                    )
                VisionService.set_status(locked_payment_plan, VisionStatus.SEND_FAILED)
                locked_payment_plan.save(update_fields=["internal_data"])
            payment_plan.internal_data = locked_payment_plan.internal_data
        raise


def send_payment_plan_to_vision_async_task(payment_plan: PaymentPlan, user_id: str) -> AsyncJob | None:
    return AsyncJob.requeue(
        instance=payment_plan,
        owner_id=user_id,
        job_name=send_payment_plan_to_vision_async_task.__name__,
        action="hope.contrib.vision.tasks.send_payment_plan_to_vision_async_task_action",
        config={"payment_plan_id": str(payment_plan.pk)},
        group_key="payment",
        description=f"Send payment plan {payment_plan.pk} to Vision",
    )


def notify_payment_plan_status_to_vision_async_task_action(job: AsyncJob) -> None:
    payment_plan = PaymentPlan.objects.select_related(
        "business_area",
        "currency",
        "financial_service_provider",
    ).get(pk=job.config["payment_plan_id"])
    VisionAPI().notify_payment_plan_status(payment_plan, job.config["vision_status"])


def notify_payment_plan_status_to_vision_async_task(
    payment_plan: PaymentPlan,
    user_id: str,
    vision_status: str,
) -> AsyncJob | None:
    return AsyncJob.requeue(
        instance=payment_plan,
        owner_id=user_id,
        job_name=f"notify_payment_plan_{vision_status.lower()}_to_vision",
        action="hope.contrib.vision.tasks.notify_payment_plan_status_to_vision_async_task_action",
        config={
            "payment_plan_id": str(payment_plan.pk),
            "vision_status": vision_status,
        },
        group_key="payment",
        description=f"Notify Vision that payment plan {payment_plan.pk} is {vision_status}",
    )
