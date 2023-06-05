import logging
from typing import Any, List, Union

from hct_mis_api.apps.utils.sentry import sentry_tags

from ..core.celery import app
from .models import Query, Report
from .utils import should_run

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
def refresh_report(self: Any, id: int) -> Union[None, List]:
    result = None
    try:
        report: Report = Report.objects.get(id=id)
        result = report.execute(run_query=True)
    except Report.DoesNotExist as e:
        logger.exception(e)
    except BaseException as e:
        logger.exception(e)
        raise self.retry(exc=e)
    return result


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@sentry_tags
def refresh_reports(self: Any) -> List:
    results = []
    try:
        for report in Report.objects.filter(active=True, frequence__isnull=False):
            if should_run(report.frequence):
                ret = report.queue()
                # ret = report.execute(run_query=True)
                results.append(ret)
            else:
                results.append([report.pk, "skip"])
    except BaseException as e:
        logger.exception(e)
        raise self.retry(exc=e)
    return results
