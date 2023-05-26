import logging
from typing import Any, Union

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.power_query.models import Query, Report
from hct_mis_api.apps.power_query.utils import should_run
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task()
@sentry_tags
def spawn(query_id: int, **kwargs: Any) -> None:
    query = Query.objects.get(pk=query_id)
    query.run(True, kwargs)


@app.task()
@sentry_tags
def complete(query_id: int, **kwargs: Any) -> None:
    query = Query.objects.get(pk=query_id)
    query.run(True, kwargs)


@app.task()
@sentry_tags
def run_background_query(query_id: int) -> Union[str, bool, None]:
    try:
        query = Query.objects.get(pk=query_id)
        query.execute_matrix()
    except BaseException as e:
        logger.exception(e)
        return False
    return "Ok"


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@sentry_tags
def refresh_reports(self: Any) -> None:
    try:
        for report in Report.objects.filter(active=True, frequence__isnull=False):
            if should_run(report.frequence):
                report.execute(run_query=True)
    except BaseException as e:
        logger.exception(e)
        raise self.retry(exc=e)
