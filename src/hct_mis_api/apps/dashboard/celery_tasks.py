import logging
import os
from datetime import timedelta
from typing import Any

from django.utils import timezone

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.models import DashReport
from hct_mis_api.apps.dashboard.services import GenerateDashReportService
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def update_dashboard_figures_every_6_hours(self: Any) -> None:
    """
    Celery task that runs every 6 hours. It checks for all business areas with households and generates
    or updates DashReports under these conditions:

    1. The business area has newly activated households and doesn't have a DashReport yet.
    2. The DashReport hasn't been updated in the last 6 hours.
    3. The DashReport is missing the associated report file.
    """
    six_hours_ago = timezone.now() - timedelta(hours=6)

    business_areas_with_households = BusinessArea.objects.using("read_only").filter(
        id__in=Household.objects.values_list("business_area", flat=True).distinct()
    )

    for business_area in business_areas_with_households:
        try:
            dash_report, created = DashReport.objects.get_or_create(business_area=business_area)

            if (
                created
                or dash_report.updated_at < six_hours_ago
                or dash_report.file is None
                or (dash_report.file and not os.path.exists(dash_report.file.path))  # File missing on disk
            ):
                if dash_report.file and not os.path.exists(dash_report.file.path):
                    logger.info(f"File missing for report: {business_area.slug}, regenerating.")

                set_sentry_business_area_tag(business_area.slug)
                dash_report.status = DashReport.IN_PROGRESS
                dash_report.save()

                service = GenerateDashReportService(dash_report)
                service.generate_report()

                dash_report.status = DashReport.COMPLETED
                dash_report.save()

        except Exception as e:
            logger.exception(f"Failed to generate DashReport for {business_area.slug}: {e}")
            dash_report.status = DashReport.FAILED
            dash_report.save()
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
    try:
        business_area = BusinessArea.objects.get(slug=business_area_slug)

        try:
            set_sentry_business_area_tag(business_area.slug)
            dash_report, _ = DashReport.objects.get_or_create(business_area=business_area)
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
