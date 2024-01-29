from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.program.signals import program_copied
from hct_mis_api.apps.program.utils import copy_program_related_data
from hct_mis_api.apps.utils.sentry import sentry_tags


@app.task()
@sentry_tags
def copy_program_task(copy_from_program_id: str, new_program_id: str) -> None:
    program = Program.objects.get(id=new_program_id)
    copy_program_related_data(copy_from_program_id, program)
    program_copied.send(sender=Program, instance=program)


@app.task()
@sentry_tags
def adjust_program_size_task(program_id: str) -> bool:
    program = Program.objects.get(id=program_id)
    program.adjust_program_size()
    program.save(
        update_fields=(
            "household_count",
            "individual_count",
        )
    )
    return True
