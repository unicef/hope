import logging
from typing import Any, Union

import celery

from .models import Query, Report
from .utils import should_run

logger = logging.getLogger(__name__)


@celery.current_app.task
def spawn(query_id: int, **kwargs: Any) -> None:
    query = Query.objects.get(pk=query_id)
    query.run(True, kwargs)


@celery.current_app.task
def complete(query_id: int, **kwargs: Any) -> None:
    query = Query.objects.get(pk=query_id)
    query.run(True, kwargs)


@celery.current_app.task
def run_background_query(query_id: int) -> Union[str, bool, None]:
    try:
        query = Query.objects.get(pk=query_id)
        query.execute_matrix()
    except BaseException as e:
        logger.exception(e)
        return False
    return "Ok"


@celery.current_app.task(bind=True, default_retry_delay=60, max_retries=3)
def refresh_reports(self: Any) -> None:
    try:
        for report in Report.objects.filter(active=True, frequence__isnull=False):
            if should_run(report.frequence):
                report.execute(run_query=True)
    except BaseException as e:
        logger.exception(e)
        raise self.retry(exc=e)
