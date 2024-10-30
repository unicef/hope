from typing import Callable
from unittest.mock import patch

import pytest

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
    senegal = BusinessArea(slug="senegal", active=True)
    mock_business_area_objects.using.return_value.filter.return_value = [senegal]

    update_dashboard_figures.apply()
    mock_refresh_data.assert_any_call("senegal")


@pytest.mark.django_db(databases=["default", "read_only"])
def test_generate_dash_report_task(mocker: Callable[..., None], afghanistan: Callable) -> None:
    """
    Test that generate_dash_report_task refreshes data for the given business area.
    """
    mock_refresh_data = mocker.patch.object(DashboardDataCache, "refresh_data")
    generate_dash_report_task.apply(args=[afghanistan.slug])
    mock_refresh_data.assert_called_once_with(afghanistan.slug)
