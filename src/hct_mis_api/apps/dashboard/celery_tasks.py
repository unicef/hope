import logging
from typing import Any

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def generate_daily_reports(self: Any) -> None:
    """
    Celery task to generate daily reports for all DashReports with the status 'IN_PROGRESS'.

    This task iterates through all reports in the 'IN_PROGRESS' status and attempts to generate
    the report using the GenerateDashReportService. If any exception occurs, it retries the task
    up to a maximum number of retries.

    Args:
        self (Any): Reference to the Celery task instance.

    Raises:
        self.retry: Retries the task in case of failure.
    """
    from hct_mis_api.apps.dashboard.models import DashReport
    from hct_mis_api.apps.dashboard.services import GenerateDashReportService

    reports = DashReport.objects.filter(status=DashReport.IN_PROGRESS)

    for report in reports:
        try:
            set_sentry_business_area_tag(report.business_area.slug)
            service = GenerateDashReportService(report)
            service.generate_report()

        except Exception as e:
            logger.exception(e)
            raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def generate_dash_report_task(self: Any, business_area_slug: str) -> None:
    """
    Celery task to generate or update a DashReport for a given business area.

    This task either creates or updates a DashReport for the specified business area. It sets the
    status of the report to 'IN_PROGRESS' while generating, and updates it to 'COMPLETED' or 'FAILED'
    depending on the result. If an error occurs, it retries the task.

    Args:
        self (Any): Reference to the Celery task instance.
        business_area_slug (str): The slug of the business area for which the report should be generated.

    Raises:
        self.retry: Retries the task in case of failure.
    """
    from hct_mis_api.apps.dashboard.models import DashReport
    from hct_mis_api.apps.dashboard.services import GenerateDashReportService

    try:
        business_area = BusinessArea.objects.get(slug=business_area_slug)

        try:
            set_sentry_business_area_tag(business_area.slug)
            dash_report, created = DashReport.objects.get_or_create(business_area=business_area)
            dash_report.status = DashReport.IN_PROGRESS
            dash_report.save()

            service = GenerateDashReportService(dash_report)
            service.generate_report()

            dash_report.status = DashReport.COMPLETED
            dash_report.save()

        except Exception as e:
            if "dash_report" in locals():
                dash_report.status = DashReport.FAILED
                dash_report.save()
            logger.error(f"Failed to generate DashReport for {business_area.name}: {e}")
            raise self.retry(exc=e, countdown=60)

    except BusinessArea.DoesNotExist:
        logger.error(f"Business area with slug {business_area_slug} not found.")
