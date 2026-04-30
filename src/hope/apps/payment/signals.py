from typing import Any

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from hope.api.caches import get_or_create_cache_key, increment_cache_key
from hope.models import PaymentPlan, PaymentPlanGroup, ProgramCycle


@receiver(post_save, sender=ProgramCycle)
def create_default_payment_plan_group(sender: Any, instance: ProgramCycle, created: bool, **kwargs: dict) -> None:
    if created:
        PaymentPlanGroup.objects.create(cycle=instance, name="Default Group")


@receiver(post_save, sender=PaymentPlanGroup)
@receiver(post_delete, sender=PaymentPlanGroup)
def increment_payment_plan_group_list_cache(sender: Any, instance: PaymentPlanGroup, **kwargs: dict) -> None:
    program = instance.cycle.program
    business_area_slug = program.business_area.slug
    program_code = program.code

    def _increment() -> None:
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        version_key = f"{business_area_slug}:{business_area_version}:{program_code}:payment_plan_groups_list"
        increment_cache_key(version_key)

    transaction.on_commit(_increment)


@receiver(post_save, sender=PaymentPlan)
def increment_payment_plan_version_cache(sender: Any, instance: PaymentPlan, created: bool, **kwargs: dict) -> None:
    if instance.status in [
        PaymentPlan.Status.IN_APPROVAL,
        PaymentPlan.Status.IN_AUTHORIZATION,
        PaymentPlan.Status.IN_REVIEW,
        PaymentPlan.Status.ACCEPTED,
    ]:
        business_area_slug = instance.business_area.slug

        def _increment() -> None:
            business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
            version_key = f"{business_area_slug}:{business_area_version}:management_payment_plans_list"
            increment_cache_key(version_key)

        transaction.on_commit(_increment)
