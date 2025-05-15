import logging
from typing import Any

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.services import DashboardDataCache, DashboardGlobalDataCache
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)



@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def update_dashboard_figures(self: Any) -> None:
    """
    Celery task that runs every 6 hours to refresh dashboard data for allactive BA.
    """
    business_areas_with_households = BusinessArea.objects.using("read_only").filter(active=True)

    for business_area in business_areas_with_households:
        try:
            set_sentry_business_area_tag(business_area.slug)
            DashboardDataCache.refresh_data(business_area.slug)

        except Exception as e:
            raise self.retry(exc=e)
    DashboardGlobalDataCache.refresh_data()


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def generate_dash_report_task(self: Any, business_area_slug: str) -> None:
    """
    Celery task to refresh dashboard data for a specific business area.
    """
    try:
        business_area = BusinessArea.objects.using("read_only").get(slug=business_area_slug)
        set_sentry_business_area_tag(business_area.slug)
        DashboardDataCache.refresh_data(business_area.slug)

    except BusinessArea.DoesNotExist:
        raise ValueError(f"Business area with slug {business_area_slug} not found.")
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
