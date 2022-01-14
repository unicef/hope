import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.transaction import atomic
from django.urls import reverse
from django.utils import timezone

from celery.app import default_app

from .models import Query, Report

logger = logging.getLogger(__name__)


@default_app.task()
def queue(query_id):
    try:
        with atomic():
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


@default_app.task()
def reporting(query_id):
    try:
        for report in Report.objects.filter(refresh=True):
            with atomic():
                report.last_run = timezone.now()
                report.query.execute(True)
                report.output

    except Exception as e:
        logger.exception(e)
