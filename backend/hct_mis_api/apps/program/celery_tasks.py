from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.program.utils import copy_program_related_data
from hct_mis_api.apps.utils.sentry import sentry_tags


@app.task()
@sentry_tags
def copy_program_task(copy_from_program_id: str, new_program_id: str) -> None:
    program = Program.objects.get(id=new_program_id)
    copy_program_related_data(copy_from_program_id, program)
