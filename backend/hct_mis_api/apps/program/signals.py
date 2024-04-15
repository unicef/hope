from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.program.utils import create_program_partner_access, remove_program_partner_access

program_copied = Signal()


def adjust_program_size(program: Program) -> None:
    from hct_mis_api.apps.program.celery_tasks import adjust_program_size_task

    transaction.on_commit(lambda: adjust_program_size_task.delay(program.id))


@receiver(post_save, sender=Program)
def handle_partner_access_change(sender, instance, **kwargs):
    partner_access = instance.partner_access
    if partner_access == Program.ALL_PARTNERS_ACCESS:
        create_program_partner_access([], instance, partner_access)
    elif partner_access == Program.NONE_PARTNERS_ACCESS:
        remove_program_partner_access([], instance)
        create_program_partner_access([], instance, partner_access)
