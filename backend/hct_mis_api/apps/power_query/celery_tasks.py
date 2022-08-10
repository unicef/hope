import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.transaction import atomic
from django.urls import reverse
from django.utils import timezone

from hct_mis_api.apps.utils.sentry import sentry_tags

from ..core.celery import app
from .models import Query, Report

logger = logging.getLogger(__name__)


@app.task()
@sentry_tags
def queue(query_id):
    try:
        query = Query.objects.get(pk=query_id)
        result = query.execute(persist=True)
        if result:
            url = reverse("admin:power_query_dataset_export", args=[query.dataset.pk])
            send_mail(
                "Power Query completed",
                f"""Power Query {query.name} completed.
results available here: {url}.

""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[query.owner.email],
            )
    except Exception as e:
        logger.exception(e)
        return False
    return result


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
