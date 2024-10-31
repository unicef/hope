from typing import Callable
from unittest.mock import patch

import pytest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.celery_tasks import (
    generate_dash_report_task,
    update_dashboard_figures,
)
from hct_mis_api.apps.dashboard.services import DashboardDataCache


@pytest.mark.django_db(databases=["default", "read_only"])
@patch.object(DashboardDataCache, "refresh_data")
@patch("hct_mis_api.apps.core.models.BusinessArea.objects")
def test_update_dashboard_figures(mock_business_area_objects: patch, mock_refresh_data: patch) -> None:  # type: ignore
    """
    Test that update_dashboard_figures refreshes data for all active business areas.
    """
    afghanistan = BusinessArea(slug="afghanistan", active=True)
    mock_business_area_objects.using.return_value.filter.return_value = [afghanistan]

    update_dashboard_figures.apply()
    mock_refresh_data.assert_any_call("afghanistan")


@pytest.mark.django_db(databases=["default", "read_only"])
def test_generate_dash_report_task(mocker: Callable[..., None], afghanistan: Callable) -> None:
    """
    Test that generate_dash_report_task refreshes data for the given business area.
    """
    mock_refresh_data = mocker.patch.object(DashboardDataCache, "refresh_data")
    generate_dash_report_task.apply(args=[afghanistan.slug])
    mock_refresh_data.assert_called_once_with(afghanistan.slug)


@pytest.mark.django_db(databases=["default", "read_only"])
@patch.object(DashboardDataCache, "refresh_data", side_effect=Exception("Mocked error"))
@patch("hct_mis_api.apps.dashboard.celery_tasks.logger")
def test_update_dashboard_figures_retry_on_failure(mock_logger: Callable[..., None], afghanistan: Callable) -> None:
    with patch("celery.app.task.Task.retry", side_effect=Exception("Retry")):
        try:
            update_dashboard_figures.apply()
        except Exception:
            pass

    mock_logger.exception.assert_called_with(f"Failed to refresh dashboard data for {afghanistan.slug}: Mocked error")


@pytest.mark.django_db(databases=["default", "read_only"])
@patch("hct_mis_api.apps.dashboard.celery_tasks.logger")
def test_generate_dash_report_task_business_area_not_found(mock_logger: Callable[..., None]) -> None:
    non_existent_slug = "non-existent-area"

    generate_dash_report_task.apply(args=[non_existent_slug])

    mock_logger.error.assert_called_with(f"Business area with slug {non_existent_slug} not found.")


@pytest.mark.django_db(databases=["default", "read_only"])
@patch.object(DashboardDataCache, "refresh_data", side_effect=Exception("Mocked error"))
@patch("hct_mis_api.apps.dashboard.celery_tasks.logger")
def test_generate_dash_report_task_retry_on_failure(mock_logger: Callable[..., None]) -> None:
    business_area = BusinessAreaFactory(slug="test-area", active=True)
    with patch("celery.app.task.Task.retry", side_effect=Exception("Retry")):
        try:
            generate_dash_report_task.apply(args=[business_area.slug])
        except Exception:
            pass
    mock_logger.error.assert_called_with(f"Failed to refresh dashboard data for {business_area.slug}: Mocked error")
