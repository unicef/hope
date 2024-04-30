from typing import Any

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

# from django_redis import get_redis_connection

from hct_mis_api.apps.payment.models import PaymentPlan


@receiver(post_save, sender=PaymentPlan)
def increment_payment_plan_per_program_version(
    sender: Any, instance: PaymentPlan, created: bool, **kwargs: dict
) -> None:
    # redis_connection = get_redis_connection()
    if instance.status in [
        PaymentPlan.Status.IN_APPROVAL,
        PaymentPlan.Status.IN_AUTHORIZATION,
        PaymentPlan.Status.IN_REVIEW,
        PaymentPlan.Status.ACCEPTED,
    ]:
        business_area_slug = instance.business_area.slug
        version = cache.get(f"{business_area_slug}:management_payment_plans_list")
        if not version:
            cache.set(f"{business_area_slug}:management_payment_plans_list", 1)
        else:
            cache.incr(f"{business_area_slug}:management_payment_plans_list")
        # redis_connection.hincrby(business_area_slug, "management_payment_plans_list", 1)
