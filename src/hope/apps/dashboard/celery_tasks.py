from datetime import date
import logging

from django.conf import settings
from django.core.cache import cache
from django.db import OperationalError, ProgrammingError
import psycopg2

from hope.apps.core.celery import app
from hope.apps.dashboard.services import (
    GLOBAL_SLUG,
    DashboardDataCache,
    DashboardGlobalDataCache,
)
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag
from hope.models import BusinessArea

logger = logging.getLogger(__name__)


@app.task(
    autoretry_for=(OperationalError, ProgrammingError, psycopg2.errors.InvalidCursorName),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
@log_start_and_end
@sentry_tags
def update_dashboard_figures() -> None:
    """Celery task that runs periodically (e.g., daily) to refresh all dashboard data."""
    business_areas_with_households = BusinessArea.objects.using(settings.DASHBOARD_DB).filter(active=True)

    for business_area in business_areas_with_households:
        set_sentry_business_area_tag(business_area.slug)
        DashboardDataCache.refresh_data(business_area.slug)
        cache.delete(f"dash_report_task_running_{business_area.slug}")

    set_sentry_business_area_tag("global")
    DashboardGlobalDataCache.refresh_data()
    cache.delete(f"dash_report_task_running_{GLOBAL_SLUG}")


@app.task(
    autoretry_for=(OperationalError, ProgrammingError, psycopg2.errors.InvalidCursorName),
    retry_kwargs={"max_retries": 3, "countdown": 300},
)
@log_start_and_end
@sentry_tags
def update_recent_dashboard_figures() -> None:
    """Celery task to refresh dashboard data for recent years (current and previous).

    Runs more frequently (e.g., hourly).
    """
    current_year = date.today().year
    previous_year = current_year - 1
    years_to_refresh = [current_year, previous_year]

    for ba in BusinessArea.objects.using(settings.DASHBOARD_DB).filter(active=True):
        set_sentry_business_area_tag(ba.slug)
        try:
            DashboardDataCache.refresh_data(ba.slug, years_to_refresh=years_to_refresh)
            cache.delete(f"dash_report_task_running_{ba.slug}")
        except Exception as e:
            logger.error(
                f"Error refreshing recent dashboard data for {ba.slug}: {e}",
                exc_info=True,
            )

    set_sentry_business_area_tag("global")
    try:
        DashboardGlobalDataCache.refresh_data(years_to_refresh=years_to_refresh)
        cache.delete(f"dash_report_task_running_{GLOBAL_SLUG}")
    except Exception as e:
        logger.error(f"Error refreshing recent global dashboard data: {e}", exc_info=True)


@app.task(
    autoretry_for=(OperationalError, ProgrammingError, psycopg2.errors.InvalidCursorName),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
@log_start_and_end
@sentry_tags
def generate_dash_report_task(business_area_slug: str) -> None:
    """Celery task to refresh dashboard data for a specific business area (full refresh) or the global dashboard."""
    if business_area_slug == GLOBAL_SLUG:
        set_sentry_business_area_tag(GLOBAL_SLUG)
        DashboardGlobalDataCache.refresh_data()
    else:
        try:
            business_area = BusinessArea.objects.using(settings.DASHBOARD_DB).get(slug=business_area_slug)
        except BusinessArea.DoesNotExist:
            logger.error(
                f"Dashboard report generation failed: Business area with slug '{business_area_slug}' not found."
            )
            return
        set_sentry_business_area_tag(business_area.slug)
        DashboardDataCache.refresh_data(business_area.slug)

    cache.delete(f"dash_report_task_running_{business_area_slug}")
