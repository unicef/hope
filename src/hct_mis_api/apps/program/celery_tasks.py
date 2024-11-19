from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.periodic_data_update.utils import (
    populate_pdu_new_rounds_with_null_values,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.program.signals import program_copied
from hct_mis_api.apps.program.utils import copy_program_related_data
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag


@app.task()
@sentry_tags
@log_start_and_end
def copy_program_task(copy_from_program_id: str, new_program_id: str, user_id: str) -> None:
    program = Program.objects.get(id=new_program_id)
    set_sentry_business_area_tag(program.business_area.name)
    copy_program_related_data(copy_from_program_id, program, user_id)
    program_copied.send(sender=Program, instance=program)


@app.task()
@sentry_tags
@log_start_and_end
def adjust_program_size_task(program_id: str) -> bool:
    program = Program.objects.get(id=program_id)
    set_sentry_business_area_tag(program.business_area.name)
    program.adjust_program_size()
    program.save(
        update_fields=(
            "household_count",
            "individual_count",
        )
    )
    return True


@app.task()
@sentry_tags
@log_start_and_end
def populate_pdu_new_rounds_with_null_values_task(program_id: str) -> bool:
    program = Program.objects.get(id=program_id)
    set_sentry_business_area_tag(program.business_area.name)
    populate_pdu_new_rounds_with_null_values(program)
    return True
