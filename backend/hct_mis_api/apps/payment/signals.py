from typing import Any

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from hct_mis_api.apps.payment.models import PaymentPlan


@receiver(post_save, sender=PaymentPlan)
def increment_payment_plan_per_business_area_version(
    sender: Any, instance: PaymentPlan, created: bool, **kwargs: dict
) -> None:
    if instance.status in [
        PaymentPlan.Status.IN_APPROVAL,
        PaymentPlan.Status.IN_AUTHORIZATION,
        PaymentPlan.Status.IN_REVIEW,
        PaymentPlan.Status.ACCEPTED,
    ]:
        program_id = instance.program.id
        current_version = cache.get(f"payment_plan_version_for_program_{program_id}", 0)
        cache.set(f"payment_plan_version_for_program_{program_id}", value=int(current_version) + 1, timeout=None)
