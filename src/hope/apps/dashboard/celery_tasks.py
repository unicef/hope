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
        lock_key = f"dash_report_task_running_{business_area.slug}"
        lock_acquired = cache.add(lock_key, True, timeout=60 * 60)
        try:
            DashboardDataCache.refresh_data(business_area.slug)
        finally:
            if lock_acquired:
                cache.delete(lock_key)

    set_sentry_business_area_tag("global")
    global_lock_key = f"dash_report_task_running_{GLOBAL_SLUG}"
    global_lock_acquired = cache.add(global_lock_key, True, timeout=60 * 60)
    try:
        DashboardGlobalDataCache.refresh_data()
    finally:
        if global_lock_acquired:
            cache.delete(global_lock_key)


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
        lock_key = f"dash_report_task_running_{ba.slug}"
        lock_acquired = cache.add(lock_key, True, timeout=60 * 15)
        try:
            DashboardDataCache.refresh_data(ba.slug, years_to_refresh=years_to_refresh)
        except Exception as e:
            logger.error(
                f"Error refreshing recent dashboard data for {ba.slug}: {e}",
                exc_info=True,
            )
        finally:
            if lock_acquired:
                cache.delete(lock_key)

    set_sentry_business_area_tag("global")
    global_lock_key = f"dash_report_task_running_{GLOBAL_SLUG}"
    global_lock_acquired = cache.add(global_lock_key, True, timeout=60 * 60)
    try:
        DashboardGlobalDataCache.refresh_data(years_to_refresh=years_to_refresh)
    except Exception as e:
        logger.error(f"Error refreshing recent global dashboard data: {e}", exc_info=True)
    finally:
        if global_lock_acquired:
            cache.delete(global_lock_key)


@app.task(bind=True)
@log_start_and_end
@sentry_tags
def generate_dash_report_task(self, business_area_slug: str) -> None:
    """Celery task to refresh dashboard data for a specific business area (full refresh) or the global dashboard."""
    is_retrying = False
    try:
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
    except (OperationalError, ProgrammingError, psycopg2.errors.InvalidCursorName) as exc:
        if self.request.retries < 3:
            is_retrying = True
            raise self.retry(exc=exc, countdown=60)
        raise
    finally:
        if not is_retrying:
            cache.delete(f"dash_report_task_running_{business_area_slug}")
