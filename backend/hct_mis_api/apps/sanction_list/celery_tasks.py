import logging

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end

logger = logging.getLogger(__name__)


@app.task
@log_start_and_end
def sync_sanction_list_task():
    try:
        from hct_mis_api.apps.sanction_list.tasks.load_xml import (
            LoadSanctionListXMLTask,
        )

        LoadSanctionListXMLTask().execute()
    except Exception as e:
        logger.exception(e)
        raise


@app.task
def check_against_sanction_list_task(uploaded_file_id, original_file_name):
    try:
        from hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list import (
            CheckAgainstSanctionListTask,
        )

        CheckAgainstSanctionListTask().execute(
            uploaded_file_id=uploaded_file_id,
            original_file_name=original_file_name,
        )
    except Exception as e:
        logger.exception(e)
        raise
