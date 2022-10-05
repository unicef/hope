import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.transaction import atomic
from django.urls import reverse
from django.utils import timezone

from celery.canvas import chord

from hct_mis_api.apps.utils.sentry import sentry_tags

from ..core.celery import app
from .models import Query, Report

logger = logging.getLogger(__name__)


@app.task()
@sentry_tags
def spawn(query_id, **kwargs):
    query = Query.objects.get(pk=query_id)
    query.run(True, kwargs)


@app.task()
@sentry_tags
def complete(query_id, **kwargs):
    query = Query.objects.get(pk=query_id)
    query.run(True, kwargs)


@app.task()
@sentry_tags
def queue(query_id, **kwargs):
    try:
        query = Query.objects.get(pk=query_id)
        if query.parametrizer:
            args = query.parametrizer.get_matrix()
        else:
            args = []
        chord([spawn.s(persist=True, **a) for a in args])(complete.si(query_id))
    except Exception as e:
        logger.exception(e)
        return False
    return "Ok"


@app.task()
@sentry_tags
def refresh_reports():
    try:
        for report in Report.objects.filter(refresh=True):
            with atomic():
                report.last_run = timezone.now()
                report.execute()
                url = reverse("admin:power_query_report_view", args=[report.pk])
                send_mail(
                    f"Report {report.name} refreshed",
                    f"""Report {report.name} hase been refreshed.
It can be downloaded here: {url}.
    
""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[u.email for u in report.notify_to],
                )
    except Exception as e:
        logger.exception(e)
