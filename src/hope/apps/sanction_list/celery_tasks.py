import logging
from typing import Any
from uuid import UUID

from hope.apps.core.celery import app
from models.sanction_list import SanctionList
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@sentry_tags
def sync_sanction_list_task(self: Any) -> None:
    for sl in SanctionList.objects.all():
        sl.refresh()


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def check_against_sanction_list_task(self: Any, uploaded_file_id: UUID, original_file_name: str) -> None:
    try:
        from hope.apps.sanction_list.tasks.check_against_sanction_list import (
            CheckAgainstSanctionListTask,
        )

        CheckAgainstSanctionListTask().execute(
            uploaded_file_id=uploaded_file_id,
            original_file_name=original_file_name,
        )
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)
