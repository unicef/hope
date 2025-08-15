import logging
from datetime import date
from typing import Any

from hope.apps.core.celery import app
from hope.apps.core.models import BusinessArea
from hope.apps.dashboard.services import (
    GLOBAL_SLUG,
    DashboardDataCache,
    DashboardGlobalDataCache,
)
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def update_dashboard_figures(self: Any) -> None:
    """Celery task that runs periodically (e.g., daily) to refresh all dashboard data."""
    business_areas_with_households = BusinessArea.objects.using("read_only").filter(active=True)

    for business_area in business_areas_with_households:
        set_sentry_business_area_tag(business_area.slug)
        DashboardDataCache.refresh_data(business_area.slug)

    set_sentry_business_area_tag("global")
    DashboardGlobalDataCache.refresh_data()


@app.task(bind=True, default_retry_delay=300, max_retries=3)
@log_start_and_end
@sentry_tags
def update_recent_dashboard_figures(self: Any) -> None:
    """Celery task to refresh dashboard data for recent years (current and previous).

    Runs more frequently (e.g., hourly).
    """
    current_year = date.today().year
    previous_year = current_year - 1
    years_to_refresh = [current_year, previous_year]

    active_business_areas = list(BusinessArea.objects.using("read_only").filter(active=True))
    for ba in active_business_areas:
        try:
            set_sentry_business_area_tag(ba.slug)
            DashboardDataCache.refresh_data(ba.slug, years_to_refresh=years_to_refresh)
        except Exception as e:
            logger.error(f"Error refreshing recent dashboard data for {ba.slug}: {e}", exc_info=True)

    try:
        set_sentry_business_area_tag("global")
        DashboardGlobalDataCache.refresh_data(years_to_refresh=years_to_refresh)
    except Exception as e:
        logger.error(f"Error refreshing recent global dashboard data: {e}", exc_info=True)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def generate_dash_report_task(self: Any, business_area_slug: str) -> None:
    """Celery task to refresh dashboard data for a specific business area (full refresh) or the global dashboard."""
    if business_area_slug == GLOBAL_SLUG:
        set_sentry_business_area_tag(GLOBAL_SLUG)
        DashboardGlobalDataCache.refresh_data()
    else:
        try:
            business_area = BusinessArea.objects.using("read_only").get(slug=business_area_slug)
        except BusinessArea.DoesNotExist:
            logger.error(
                f"Dashboard report generation failed: Business area with slug '{business_area_slug}' not found."
            )
            return
        set_sentry_business_area_tag(business_area.slug)
        DashboardDataCache.refresh_data(business_area.slug)
