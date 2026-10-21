from django.db import transaction
from django.utils import timezone

from hope.contrib.vision.api import VisionAPI, VisionAPIError, VisionAPIMissingCredentialsError
from hope.contrib.vision.choices import VISION_SEND_MUTABLE_STATUSES, VisionLogEntryType, VisionStatus
from hope.contrib.vision.services import VisionService
from hope.models import AsyncJob, PaymentPlanGroup


def send_payment_plan_group_to_vision_async_task_action(job: AsyncJob) -> None:
    with transaction.atomic():
        group = (
            PaymentPlanGroup.objects.select_for_update()
            .select_related("cycle__program__business_area", "financial_service_provider", "currency")
            .get(pk=job.config["payment_plan_group_id"])
        )
        if not group.can_send_to_vision:
            return

        # Lock and recheck immediately before marking the request in flight. This prevents an older task instance
        # from restoring the Vision attempt after an abort or rejection has reset it.
        VisionService.set_status(group, VisionStatus.WAITING_FOR_CALLBACK)
        group.save(update_fields=["internal_data"])

    try:
        VisionAPI().send_payment_plan_group(group)
    except (VisionAPIError, VisionAPIMissingCredentialsError) as error:
        with transaction.atomic():
            locked_group = PaymentPlanGroup.objects.select_for_update().get(pk=group.pk)
            if (
                locked_group.status == PaymentPlanGroup.Status.IN_REVIEW
                and locked_group.vision_status in VISION_SEND_MUTABLE_STATUSES
            ):
                if locked_group.vision_status != VisionStatus.SEND_FAILED.value:
                    VisionService.vision_data(locked_group).setdefault("log", []).append(
                        {
                            "timestamp": timezone.now().isoformat(),
                            "type": VisionLogEntryType.API_CALL.value,
                            "payload": {},
                            "response": {"error": type(error).__name__},
                        }
                    )
                VisionService.set_status(locked_group, VisionStatus.SEND_FAILED)
                locked_group.save(update_fields=["internal_data"])
            group.internal_data = locked_group.internal_data
        raise


def send_payment_plan_group_to_vision_async_task(group: PaymentPlanGroup, user_id: str) -> AsyncJob | None:
    return AsyncJob.requeue(
        instance=group,
        owner_id=user_id,
        job_name=send_payment_plan_group_to_vision_async_task.__name__,
        action="hope.contrib.vision.tasks.send_payment_plan_group_to_vision_async_task_action",
        config={"payment_plan_group_id": str(group.pk)},
        group_key="payment",
        description=f"Send Payment Plan Group {group.pk} to Vision",
    )


def notify_payment_plan_group_status_to_vision_async_task_action(job: AsyncJob) -> None:
    group = PaymentPlanGroup.objects.select_related(
        "cycle__program__business_area", "currency", "financial_service_provider"
    ).get(pk=job.config["payment_plan_group_id"])
    VisionAPI().notify_payment_plan_group_status(group, job.config["vision_status"])


def notify_payment_plan_group_status_to_vision_async_task(
    group: PaymentPlanGroup,
    user_id: str,
    vision_status: str,
) -> AsyncJob | None:
    return AsyncJob.requeue(
        instance=group,
        owner_id=user_id,
        job_name=f"notify_payment_plan_group_{vision_status.lower()}_to_vision",
        action="hope.contrib.vision.tasks.notify_payment_plan_group_status_to_vision_async_task_action",
        config={
            "payment_plan_group_id": str(group.pk),
            "vision_status": vision_status,
        },
        group_key="payment",
        description=f"Notify Vision that Payment Plan Group {group.pk} is {vision_status}",
    )
