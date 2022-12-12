import logging
from typing import Any, Union

from django.db.transaction import atomic
from django.utils import timezone

from hct_mis_api.apps.utils.sentry import sentry_tags

from ..core.celery import app
from .models import Query, Report

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
def run_background_query(query_id: int, **kwargs: Any) -> Union[str, bool, None]:
    try:
        query = Query.objects.get(pk=query_id)
        query.execute_matrix()
    except Exception as e:
        logger.exception(e)
        return False
    return "Ok"


@app.task()
@sentry_tags
def refresh_reports() -> None:
    try:
        for report in Report.objects.filter(active=True, refresh_daily=True):
            run_background_query.delay(report.query.id)
            with atomic():
                report.last_run = timezone.now()
                report.execute()
    except Exception as e:
        logger.exception(e)
