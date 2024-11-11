import logging
from typing import Callable, Generator
from unittest.mock import patch

import pytest

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.celery_tasks import (
    generate_dash_report_task,
    update_dashboard_figures,
)
from hct_mis_api.apps.dashboard.services import DashboardDataCache


@pytest.mark.django_db(databases=["default", "read_only"])
def test_update_dashboard_figures(populate_dashboard_cache: Callable, afghanistan: BusinessArea) -> None:
    """
    Test that update_dashboard_figures refreshes data for all active business areas.
    """
    populate_dashboard_cache(afghanistan)
    update_dashboard_figures.apply()
    data = DashboardDataCache.get_data("afghanistan")
    assert data is not None


@pytest.mark.django_db(databases=["default", "read_only"])
def test_generate_dash_report_task(afghanistan: BusinessArea) -> None:
    """
    Test that generate_dash_report_task refreshes data for the given business area.
    """

    generate_dash_report_task.apply(args=[afghanistan.slug])
    data = DashboardDataCache.get_data(afghanistan.slug)
    assert data is not None


@pytest.mark.django_db(databases=["default", "read_only"])
def test_generate_dash_report_task_business_area_not_found(caplog: Generator) -> None:
    """
    Test that generate_dash_report_task logs an error if the business area is not found.
    """
    non_existent_slug = "non-existent-area"

    with caplog.at_level("ERROR"):
        generate_dash_report_task.apply(args=[non_existent_slug])
        assert f"Business area with slug {non_existent_slug} not found." in caplog.text


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
def test_update_dashboard_figures_retry_on_failure(caplog: Generator, afghanistan: BusinessArea) -> None:
    """
    Test that update_dashboard_figures retries on failure and logs an exception.
    """
    with caplog.at_level(logging.ERROR):
        with patch(
            "hct_mis_api.apps.dashboard.services.DashboardDataCache.refresh_data", side_effect=Exception("Mocked error")
        ):
            try:
                update_dashboard_figures.apply(throw=True)  # Using throw to catch the retry error
            except Exception:
                pass
    assert "Failed to refresh dashboard data" in caplog.text
