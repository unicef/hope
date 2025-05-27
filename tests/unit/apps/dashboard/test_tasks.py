from typing import Callable
from unittest.mock import patch

import pytest

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.celery_tasks import (generate_dash_report_task,
                                                     update_dashboard_figures)
from hct_mis_api.apps.dashboard.services import DashboardDataCache


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
def test_generate_dash_report_task(afghanistan: BusinessArea, populate_dashboard_cache: Callable) -> None:
    """
    Test that generate_dash_report_task refreshes data for the given business area.
    """
    populate_dashboard_cache(afghanistan)
    generate_dash_report_task.apply(args=[afghanistan.slug])
    data = DashboardDataCache.get_data(afghanistan.slug)
    assert data is not None


@pytest.mark.django_db(databases=["default", "read_only"])
def test_generate_dash_report_task_business_area_not_found() -> None:
    """
    Test that generate_dash_report_task logs an error if the business area is not found.
    """
    non_existent_slug = "non-existent-area"

    with pytest.raises(ValueError, match=f"Business area with slug {non_existent_slug} not found."):
        generate_dash_report_task(business_area_slug=non_existent_slug)


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
def test_update_dashboard_figures_retry_on_failure(afghanistan: BusinessArea) -> None:
    """
    Test that update_dashboard_figures retries on failure.
    """
    mocked_error_message = "Mocked error"

    with patch(
        "hct_mis_api.apps.dashboard.services.DashboardDataCache.refresh_data",
        side_effect=Exception(mocked_error_message),
    ):
        with pytest.raises(Exception, match=mocked_error_message):
            update_dashboard_figures.apply(throw=True)
