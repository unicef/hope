from django.db import transaction
from django.dispatch import Signal

from hct_mis_api.apps.program.models import Program

program_copied = Signal()


def adjust_program_size(program: Program) -> None:
    from hct_mis_api.apps.program.celery_tasks import adjust_program_size_task

    transaction.on_commit(lambda: adjust_program_size_task.delay(program.id))
