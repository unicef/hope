from typing import Callable
from unittest.mock import patch

import pytest

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.celery_tasks import (
    generate_dash_report_task,
    update_dashboard_figures,
)
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
        "hct_mis_api.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data",
        side_effect=Exception(mocked_error_message),
    ) as mock_data_refresh:
        if not BusinessArea.objects.filter(slug=afghanistan.slug, active=True).exists():
            afghanistan.active = True
            afghanistan.save()

        with pytest.raises(Exception, match=mocked_error_message):
            update_dashboard_figures.apply(throw=True)
        mock_data_refresh.assert_called_with(afghanistan.slug)


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
def test_update_dashboard_figures_retry_on_global_failure(afghanistan: BusinessArea) -> None:
    """
    Test that update_dashboard_figures retries on failure of global data refresh.
    """
    mocked_error_message = "Mocked global error"
    with patch("hct_mis_api.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data") as mock_ba_refresh, patch(
        "hct_mis_api.apps.dashboard.celery_tasks.DashboardGlobalDataCache.refresh_data",
        side_effect=Exception(mocked_error_message),
    ) as mock_global_refresh:
        if not BusinessArea.objects.filter(slug=afghanistan.slug, active=True).exists():
            afghanistan.active = True
            afghanistan.save()
        else:
            BusinessArea.objects.filter(slug=afghanistan.slug).update(active=True)

        with pytest.raises(Exception, match=mocked_error_message):
            update_dashboard_figures.apply(throw=True)

        active_bas_count = BusinessArea.objects.filter(active=True).count()
        assert mock_ba_refresh.call_count == active_bas_count
        mock_global_refresh.assert_called_once()


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
def test_generate_dash_report_task_retry_on_failure(afghanistan: BusinessArea) -> None:
    """
    Test that generate_dash_report_task retries on failure.
    """
    mocked_error_message = "Mocked task error"
    with patch(
        "hct_mis_api.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data",
        side_effect=Exception(mocked_error_message),
    ) as mock_refresh:
        with pytest.raises(Exception, match=mocked_error_message):
            generate_dash_report_task.apply(args=[afghanistan.slug], throw=True)
        mock_refresh.assert_called_once_with(afghanistan.slug)
