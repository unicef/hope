import logging
from typing import Any, Dict, Tuple, Type, Union

from billiard.einfo import ExceptionInfo
from celery import Task
from sentry_sdk import capture_exception

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.power_query.models import Query, QueryResult, Report, ReportResult
from hct_mis_api.apps.power_query.utils import should_run
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


class AbstractPowerQueryTask(Task):
    model: Union[Type[Query], Type[Report]]

    def on_success(self, retval: Any, task_id: str, args: Tuple[Any], kwargs: Dict[str, Any]) -> None:
        """
        retval (Any): The return value of the task.
        task_id (str): Unique id of the executed task.
        args (Tuple): Original arguments for the executed task.
        kwargs (Dict): Original keyword arguments for the executed task.
        """
        pass

    def on_failure(
        self, exc: Exception, task_id: str, args: Tuple[Any], kwargs: Dict[str, Any], einfo: ExceptionInfo
    ) -> None:
        """
        exc (Exception): The exception raised by the task.
        task_id (str): Unique id of the failed task.
        args (Tuple): Original arguments for the task that failed.
        kwargs (Dict): Original keyword arguments for the task that failed.
        einfo (~billiard.einfo.ExceptionInfo): Exception information.
        """
        q = self.model.objects.get(id=args[0])
        sid = capture_exception(exc)
        q.sentry_error_id = sid
        q.error_message = str(exc)
        q.save()


class PowerQueryTask(AbstractPowerQueryTask):
    model = Query


class ReportTask(AbstractPowerQueryTask):
    model = Report


@app.task(base=PowerQueryTask)
@sentry_tags
def run_background_query(query_id: int) -> QueryResult:
    try:
        query = Query.objects.get(pk=query_id)
        return query.execute_matrix()
    except BaseException as e:
        logger.exception(e)
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3, base=ReportTask)
@sentry_tags
def refresh_report(self: Any, id: int) -> ReportResult:
    result: ReportResult = []
    try:
        report: Report = Report.objects.get(id=id)
        result = report.execute(run_query=True)
    except Report.DoesNotExist as e:
        logger.exception(e)
    except BaseException as e:
        logger.exception(e)
        raise self.retry(exc=e)
    return result


@app.task(bind=True, default_retry_delay=60, max_retries=3, base=ReportTask)
@sentry_tags
def refresh_reports(self: Any) -> Any:
    results: Any = []
    report: Report
    try:
        for report in Report.objects.filter(active=True, frequence__isnull=False):
            if should_run(report.frequence):
                ret = report.queue()
                results.append(ret)
            else:
                results.append([report.pk, "skip"])
    except BaseException as e:
        logger.exception(e)
        raise self.retry(exc=e)
    return results
