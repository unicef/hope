from typing import Any

from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from hct_mis_api.api.caches import get_or_create_cache_key
from hct_mis_api.apps.payment.models import PaymentPlan


@receiver(post_save, sender=PaymentPlan)
def increment_payment_plan_version_cache(sender: Any, instance: PaymentPlan, created: bool, **kwargs: dict) -> None:
    if instance.status in [
        PaymentPlan.Status.IN_APPROVAL,
        PaymentPlan.Status.IN_AUTHORIZATION,
        PaymentPlan.Status.IN_REVIEW,
        PaymentPlan.Status.ACCEPTED,
    ]:
        business_area_slug = instance.business_area.slug
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

        version_key = f"{business_area_slug}:{business_area_version}:management_payment_plans_list"
        get_or_create_cache_key(version_key, 0)
        cache.incr(version_key)


@receiver(post_save, sender=PaymentPlan)
@receiver(pre_delete, sender=PaymentPlan)
def increment_target_population_version_cache(sender: Any, instance: PaymentPlan, **kwargs: dict) -> None:
    if instance.status in PaymentPlan.PRE_PAYMENT_PLAN_STATUSES:
        business_area_slug = instance.business_area.slug
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

        program_id = instance.program_cycle.program.id

        version_key = f"{business_area_slug}:{business_area_version}:{program_id}:target_population_list"
        get_or_create_cache_key(version_key, 0)

        cache.incr(version_key)
