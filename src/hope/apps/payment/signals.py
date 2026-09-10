from typing import Any

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from hope.api.caches import get_or_create_cache_key, increment_cache_key
from hope.apps.payment.api.caches import (
    PAYMENT_PLAN_LIST_CACHE_KEYS,
    PAYMENT_VERIFICATION_LIST_CACHE_KEYS,
    invalidate_payment_plan_list_cache,
)
from hope.models import (
    PaymentPlan,
    PaymentPlanGroup,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    ProgramCycle,
)
from hope.models.payment_plan_purpose import PaymentPlanPurpose

MANAGERIAL_PAYMENT_PLAN_STATUSES = (
    PaymentPlan.Status.IN_APPROVAL,
    PaymentPlan.Status.IN_AUTHORIZATION,
    PaymentPlan.Status.IN_REVIEW,
    PaymentPlan.Status.ACCEPTED,
)


def _program_scope_by_cycle(program_cycle_id: Any) -> tuple[str, str] | None:
    return (
        ProgramCycle.objects.filter(pk=program_cycle_id)
        .values_list("program__business_area__slug", "program__code")
        .first()
    )


def _program_scope_by_payment_plan(payment_plan_id: Any) -> tuple[str, str] | None:
    return (
        PaymentPlan.objects.filter(pk=payment_plan_id)
        .values_list(
            "program_cycle__program__business_area__slug",
            "program_cycle__program__code",
        )
        .first()
    )


def _invalidate_lists(scope: tuple[str, str] | None, specific_view_cache_keys: tuple[str, ...]) -> None:
    if scope is None:
        return
    business_area_slug, program_code = scope
    invalidate_payment_plan_list_cache(business_area_slug, program_code, specific_view_cache_keys)


@receiver(post_save, sender=ProgramCycle)
def create_default_payment_plan_group(
    sender: Any, instance: ProgramCycle, created: bool, raw: bool = False, **kwargs: dict
) -> None:
    if created and not raw:
        PaymentPlanGroup.objects.create(cycle=instance, name="Default Group")


@receiver(post_save, sender=PaymentPlanGroup)
@receiver(post_delete, sender=PaymentPlanGroup)
def increment_payment_plan_group_list_cache(sender: Any, instance: PaymentPlanGroup, **kwargs: dict) -> None:
    if kwargs.get("raw"):
        return
    program = instance.cycle.program
    business_area_slug = program.business_area.slug
    program_code = program.code

    def _increment() -> None:
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        version_key = f"{business_area_slug}:{business_area_version}:{program_code}:payment_plan_groups_list"
        increment_cache_key(version_key)

    transaction.on_commit(_increment)


@receiver(post_save, sender=PaymentPlanPurpose)
@receiver(post_delete, sender=PaymentPlanPurpose)
def increment_payment_plan_purpose_list_cache(sender: Any, instance: PaymentPlanPurpose, **kwargs: dict) -> None:
    transaction.on_commit(lambda: increment_cache_key("payment_plan_purposes_list"))


@receiver(post_save, sender=PaymentPlan)
@receiver(post_delete, sender=PaymentPlan)
def increment_payment_plan_list_cache(sender: Any, instance: PaymentPlan, **kwargs: dict) -> None:
    if kwargs.get("raw"):
        return
    # invalidate payment plan lists
    _invalidate_lists(_program_scope_by_cycle(instance.program_cycle_id), PAYMENT_PLAN_LIST_CACHE_KEYS)

    if instance.status not in MANAGERIAL_PAYMENT_PLAN_STATUSES:
        return
    # invalidate payment plan managerial list
    business_area_slug = instance.business_area.slug

    def _increment() -> None:
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        version_key = f"{business_area_slug}:{business_area_version}:management_payment_plans_list"
        increment_cache_key(version_key)

    transaction.on_commit(_increment)


@receiver(post_save, sender=PaymentVerificationPlan)
@receiver(post_delete, sender=PaymentVerificationPlan)
@receiver(post_save, sender=PaymentVerificationSummary)
@receiver(post_delete, sender=PaymentVerificationSummary)
def increment_payment_verification_list_cache(
    sender: Any, instance: PaymentVerificationPlan | PaymentVerificationSummary, **kwargs: dict
) -> None:
    if kwargs.get("raw"):
        return
    _invalidate_lists(_program_scope_by_payment_plan(instance.payment_plan_id), PAYMENT_VERIFICATION_LIST_CACHE_KEYS)
