from datetime import date
from typing import Callable
from unittest.mock import Mock, call, patch

import pytest
from extras.test_utils.factories.account import BusinessAreaFactory

from hope.apps.core.models import BusinessArea
from hope.apps.dashboard.celery_tasks import (
    generate_dash_report_task,
    update_dashboard_figures,
    update_recent_dashboard_figures,
)
from hope.apps.dashboard.services import DashboardDataCache


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
@patch("hope.apps.dashboard.celery_tasks.logger.error")
@patch("hope.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data")
def test_generate_dash_report_task_business_area_not_found(mock_refresh_data: Mock, mock_logger_error: Mock) -> None:
    """
    Test that generate_dash_report_task logs an error and does not call refresh_data
    if the business area is not found.
    """
    non_existent_slug = "non-existent-area"
    BusinessArea.objects.filter(slug=non_existent_slug).delete()  # Ensure it doesn't exist

    generate_dash_report_task(business_area_slug=non_existent_slug)

    mock_logger_error.assert_called_once_with(
        f"Dashboard report generation failed: Business area with slug '{non_existent_slug}' not found."
    )
    mock_refresh_data.assert_not_called()


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
def test_update_dashboard_figures_retry_on_failure(afghanistan: BusinessArea) -> None:
    """
    Test that update_dashboard_figures retries on failure.
    """
    mocked_error_message = "Mocked error"

    with patch(
        "hope.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data",
        side_effect=Exception(mocked_error_message),
    ) as mock_data_refresh:
        if not BusinessArea.objects.filter(slug=afghanistan.slug, active=True).exists():
            afghanistan.active = True
            afghanistan.save()
        else:
            BusinessArea.objects.filter(slug=afghanistan.slug).update(active=True)

        with pytest.raises(Exception, match=mocked_error_message):
            update_dashboard_figures.apply(throw=True)
        mock_data_refresh.assert_any_call(afghanistan.slug)


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
def test_update_dashboard_figures_retry_on_global_failure(
    afghanistan: BusinessArea,
) -> None:
    """
    Test that update_dashboard_figures retries on failure of global data refresh.
    """
    mocked_error_message = "Mocked global error"
    with (
        patch("hope.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data") as mock_ba_refresh,
        patch(
            "hope.apps.dashboard.celery_tasks.DashboardGlobalDataCache.refresh_data",
            side_effect=Exception(mocked_error_message),
        ) as mock_global_refresh,
    ):
        if not BusinessArea.objects.filter(slug=afghanistan.slug, active=True).exists():
            afghanistan.active = True
            afghanistan.save()
        else:
            BusinessArea.objects.filter(slug=afghanistan.slug).update(active=True)

        with pytest.raises(Exception, match=mocked_error_message):
            update_dashboard_figures.apply(throw=True)

        active_bas_count = BusinessArea.objects.filter(active=True).count()
        assert mock_ba_refresh.call_count == active_bas_count
        mock_global_refresh.assert_called_once_with()


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
def test_generate_dash_report_task_retry_on_failure(afghanistan: BusinessArea) -> None:
    """
    Test that generate_dash_report_task retries on failure.
    """
    mocked_error_message = "Mocked task error"
    with patch(
        "hope.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data",
        side_effect=Exception(mocked_error_message),
    ) as mock_refresh:
        with pytest.raises(Exception, match=mocked_error_message):
            generate_dash_report_task.apply(args=[afghanistan.slug], throw=True)
        mock_refresh.assert_called_once_with(afghanistan.slug)


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
@patch("hope.apps.dashboard.celery_tasks.DashboardGlobalDataCache.refresh_data")
@patch("hope.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data")
def test_update_recent_dashboard_figures_success(
    mock_ba_refresh: Mock, mock_global_refresh: Mock, afghanistan: BusinessArea
) -> None:
    """
    Test that update_recent_dashboard_figures calls refresh_data with correct year filters.
    """
    iraq = BusinessAreaFactory.create(slug="iraq", name="Iraq", active=True)
    afghanistan.active = True
    afghanistan.save()

    BusinessArea.objects.exclude(slug__in=[afghanistan.slug, iraq.slug]).update(active=False)

    current_year = date.today().year
    previous_year = current_year - 1
    years_to_refresh = [current_year, previous_year]

    update_recent_dashboard_figures.apply()

    expected_ba_calls = [
        call(afghanistan.slug, years_to_refresh=years_to_refresh),
        call(iraq.slug, years_to_refresh=years_to_refresh),
    ]
    mock_ba_refresh.assert_has_calls(expected_ba_calls, any_order=True)
    assert mock_ba_refresh.call_count == 2

    mock_global_refresh.assert_called_once_with(years_to_refresh=years_to_refresh)


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
@patch("hope.apps.dashboard.celery_tasks.logger.error")
@patch("hope.apps.dashboard.celery_tasks.DashboardGlobalDataCache.refresh_data")
@patch("hope.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data")
def test_update_recent_dashboard_figures_ba_error_continues(
    mock_ba_refresh: Mock,
    mock_global_refresh: Mock,
    mock_logger_error: Mock,
    afghanistan: BusinessArea,
) -> None:
    """
    Test that update_recent_dashboard_figures continues if one BA refresh fails.
    """
    iraq = BusinessAreaFactory.create(slug="iraq", name="Iraq", active=True)
    afghanistan.active = True
    afghanistan.save()
    BusinessArea.objects.exclude(slug__in=[afghanistan.slug, iraq.slug]).update(active=False)

    current_year = date.today().year
    previous_year = current_year - 1
    years_to_refresh = [current_year, previous_year]

    def ba_refresh_side_effect_func(slug: str, years_to_refresh: list[int]) -> None:
        if slug == afghanistan.slug:
            raise Exception("BA refresh error for afghanistan")
        # For other BAs (e.g., iraq), the mock should behave normally (return None)
        return

    mock_ba_refresh.side_effect = ba_refresh_side_effect_func

    update_recent_dashboard_figures.apply()

    expected_ba_calls = [
        call(afghanistan.slug, years_to_refresh=years_to_refresh),
        call(iraq.slug, years_to_refresh=years_to_refresh),
    ]
    mock_ba_refresh.assert_has_calls(expected_ba_calls, any_order=True)
    assert mock_ba_refresh.call_count == 2

    mock_global_refresh.assert_called_once_with(years_to_refresh=years_to_refresh)
    mock_logger_error.assert_any_call(
        f"Error refreshing recent dashboard data for {afghanistan.slug}: BA refresh error for afghanistan",
        exc_info=True,
    )


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
@patch("hope.apps.dashboard.celery_tasks.logger.error")
@patch("hope.apps.dashboard.celery_tasks.DashboardGlobalDataCache.refresh_data")
@patch("hope.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data")
def test_update_recent_dashboard_figures_global_error_continues(
    mock_ba_refresh: Mock,
    mock_global_refresh: Mock,
    mock_logger_error: Mock,
    afghanistan: BusinessArea,
) -> None:
    """
    Test that update_recent_dashboard_figures logs error if global refresh fails but BAs were processed.
    """
    afghanistan.active = True
    afghanistan.save()
    BusinessArea.objects.exclude(slug=afghanistan.slug).update(active=False)

    current_year = date.today().year
    previous_year = current_year - 1
    years_to_refresh = [current_year, previous_year]

    mock_global_refresh.side_effect = Exception("Global refresh error")

    update_recent_dashboard_figures.apply()

    mock_ba_refresh.assert_called_once_with(afghanistan.slug, years_to_refresh=years_to_refresh)
    mock_global_refresh.assert_called_once_with(years_to_refresh=years_to_refresh)
    mock_logger_error.assert_called_once_with(
        "Error refreshing recent global dashboard data: Global refresh error",
        exc_info=True,
    )


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
@patch("hope.apps.dashboard.celery_tasks.DashboardGlobalDataCache.refresh_data")
@patch("hope.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data")
def test_update_dashboard_figures_no_active_bas(mock_ba_refresh: Mock, mock_global_refresh: Mock) -> None:
    """
    Test update_dashboard_figures when there are no active business areas.
    It should not call BA refresh but should call global refresh.
    """
    BusinessArea.objects.all().update(active=False)

    update_dashboard_figures.apply()

    mock_ba_refresh.assert_not_called()
    mock_global_refresh.assert_called_once_with()


@pytest.mark.django_db(databases=["default", "read_only"], transaction=True)
@patch("hope.apps.dashboard.celery_tasks.DashboardGlobalDataCache.refresh_data")
@patch("hope.apps.dashboard.celery_tasks.DashboardDataCache.refresh_data")
def test_update_recent_dashboard_figures_no_active_bas(mock_ba_refresh: Mock, mock_global_refresh: Mock) -> None:
    """
    Test update_recent_dashboard_figures when there are no active business areas.
    It should not call BA refresh but should call global refresh with year filters.
    """
    BusinessArea.objects.all().update(active=False)

    current_year = date.today().year
    previous_year = current_year - 1
    years_to_refresh = [current_year, previous_year]

    update_recent_dashboard_figures.apply()

    mock_ba_refresh.assert_not_called()
    mock_global_refresh.assert_called_once_with(years_to_refresh=years_to_refresh)
