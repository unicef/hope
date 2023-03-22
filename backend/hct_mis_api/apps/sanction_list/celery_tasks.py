import logging
from typing import Any
from uuid import UUID

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def sync_sanction_list_task(self: Any) -> None:
    try:
        from hct_mis_api.apps.sanction_list.tasks.load_xml import (
            LoadSanctionListXMLTask,
        )

        LoadSanctionListXMLTask().execute()
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@sentry_tags
def check_against_sanction_list_task(self: Any, uploaded_file_id: UUID, original_file_name: str) -> None:
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
        raise self.retry(exc=e)
