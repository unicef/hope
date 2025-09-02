from typing import Any

from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import Signal, receiver

from hope.api.caches import get_or_create_cache_key
from hope.apps.program.utils import (
    create_program_partner_access,
    remove_program_partner_access,
)
from hope.models.beneficiary_group import BeneficiaryGroup
from hope.models.program import Program

program_copied = Signal()


def adjust_program_size(program: Program) -> None:
    from hope.apps.program.celery_tasks import adjust_program_size_task

    transaction.on_commit(lambda: adjust_program_size_task.delay(program.id))


pre_save_partner_access_change = Signal(providing_args=["old_partner_access"])


@receiver(pre_save, sender=Program)
def track_old_partner_access(sender: Any, instance: Program, **kwargs: Any) -> None:
    old_partner_access = getattr(Program.objects.filter(pk=instance.pk).first(), "partner_access", None)

    instance.old_partner_access = old_partner_access
    pre_save_partner_access_change.send(sender=sender, instance=instance, old_partner_access=old_partner_access)


@receiver(pre_save, sender=Program)
def update_slug_on_programme_code_change(sender: Any, instance: Program, **kwargs: Any) -> None:
    """Signal to regenerate the slug if the programme_code has changed."""
    if instance.pk is None:
        return
    try:
        old_program = Program.objects.get(pk=instance.pk)
    except Program.DoesNotExist:
        return
    if instance.programme_code != old_program.programme_code:
        instance.slug = instance.generate_slug()


@receiver(post_save, sender=Program)
def handle_partner_access_change(sender: Any, instance: Program, created: bool, **kwargs: Any) -> None:
    old_partner_access = instance.old_partner_access
    new_partner_access = instance.partner_access

    if old_partner_access != new_partner_access:
        if new_partner_access == Program.ALL_PARTNERS_ACCESS:
            create_program_partner_access([], instance, new_partner_access)
        elif new_partner_access == Program.NONE_PARTNERS_ACCESS:
            remove_program_partner_access([], instance)


@receiver([post_save, post_delete], sender=BeneficiaryGroup)
def increment_beneficiary_group_version_cache(sender: Any, instance: BeneficiaryGroup, **kwargs: dict) -> None:
    version_key = "beneficiary_group_list"
    get_or_create_cache_key(version_key, 0)
    cache.incr(version_key)


@receiver([post_save, post_delete], sender=Program)
def increase_program_version_cache(sender: Any, instance: Program, **kwargs: dict) -> None:
    business_area_slug = instance.business_area.slug
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

    version_key = f"{business_area_slug}:{business_area_version}:program_list"
    get_or_create_cache_key(version_key, 0)

    cache.incr(version_key)
