from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import Signal, receiver

from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough
from hct_mis_api.apps.program.utils import (
    create_program_partner_access,
    remove_program_partner_access,
)

program_copied = Signal()


def adjust_program_size(program: Program) -> None:
    from hct_mis_api.apps.program.celery_tasks import adjust_program_size_task

    transaction.on_commit(lambda: adjust_program_size_task.delay(program.id))


pre_save_partner_access_change = Signal(providing_args=["old_partner_access"])
pre_save_full_area_access_flag_change = Signal(providing_args=["old_full_area_access_flag"])


@receiver(pre_save, sender=Program)
def track_old_partner_access(sender, instance, **kwargs):
    try:
        old_instance = Program.objects.get(pk=instance.pk)
        old_partner_access = old_instance.partner_access
    except Program.DoesNotExist:
        old_partner_access = None

    instance.old_partner_access = old_partner_access
    pre_save_partner_access_change.send(sender=sender, instance=instance, old_partner_access=old_partner_access)


@receiver(post_save, sender=Program)
def handle_partner_access_change(sender, instance, created, **kwargs):
    old_partner_access = instance.old_partner_access
    new_partner_access = instance.partner_access

    if old_partner_access != new_partner_access:
        if new_partner_access == Program.ALL_PARTNERS_ACCESS:
            create_program_partner_access([], instance, new_partner_access)
        elif new_partner_access == Program.NONE_PARTNERS_ACCESS:
            remove_program_partner_access([], instance)
            create_program_partner_access([], instance, new_partner_access)


@receiver(pre_save, sender=ProgramPartnerThrough)
def track_old_full_area_access_flag(sender, instance, **kwargs):
    try:
        old_instance = ProgramPartnerThrough.objects.get(pk=instance.pk)
        old_full_area_access_flag = old_instance.full_area_access
    except ProgramPartnerThrough.DoesNotExist:
        old_full_area_access_flag = None

    instance.old_full_area_access_flag = old_full_area_access_flag
    pre_save_full_area_access_flag_change.send(
        sender=sender, instance=instance, old_full_area_access_flag=old_full_area_access_flag
    )


@receiver(post_save, sender=ProgramPartnerThrough)
def handle_partner_full_area_access_flag(sender, instance, **kwargs):
    # Apply signal if full_area_access=True for ProgramPartnerThrough created OR full_area_access field updated
    if new_full_area_access_flag := instance.full_area_access:
        old_full_area_access_flag = instance.old_full_area_access_flag
        if old_full_area_access_flag != new_full_area_access_flag:
            full_area_access_areas = Area.objects.filter(
                area_type__country__business_areas__id=instance.program.business_area.id
            )
            instance.areas.set(full_area_access_areas)
