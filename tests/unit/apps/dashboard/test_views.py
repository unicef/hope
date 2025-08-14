from typing import Callable, Dict, Optional
from unittest.mock import Mock, patch

from django.core.cache import cache
from django.http import Http404
from django.test import RequestFactory
from django.urls import reverse

import pytest
from extras.test_utils.factories.account import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)
from rest_framework import status

from hope.apps.account.models import RoleAssignment
from hope.apps.account.permissions import Permissions
from hope.apps.core.models import BusinessArea
from hope.apps.dashboard.services import DashboardGlobalDataCache
from hope.apps.dashboard.views import DashboardReportView

pytestmark = pytest.mark.django_db(databases=["default", "read_only"])


@pytest.fixture
def setup_client(api_client: Callable, afghanistan: BusinessAreaFactory) -> Dict[str, Optional[object]]:
    """
    Sets up the client, user, and URLs needed for tests, ensuring the dashboard cache is populated.
    Resets any default permissions.
    """
    user = UserFactory(is_superuser=False, is_staff=False)
    user.user_permissions.clear()

    client = api_client(user)
    list_url = reverse("api:household-data", args=[afghanistan.slug])
    global_url = reverse("api:household-data", args=["global"])
    generate_report_url = reverse("api:generate-dashreport", args=[afghanistan.slug])
    generate_global_report_url = reverse("api:generate-dashreport", args=["global"])

    return {
        "client": client,
        "user": user,
        "business_area": afghanistan,
        "list_url": list_url,
        "global_url": global_url,
        "generate_report_url": generate_report_url,
        "generate_global_report_url": generate_global_report_url,
    }


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_data_view_permission_denied(setup_client: Dict[str, Optional[object]]) -> None:
    """
    Test that access to the dashboard data is denied for users without permissions.
    """
    client = setup_client["client"]
    list_url = setup_client["list_url"]
    response = client.get(list_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_data_view_access_granted(
    setup_client: Dict[str, Optional[object]], populate_dashboard_cache: Callable
) -> None:
    """
    Test that access to the dashboard data is granted for users with permissions.
    """
    client = setup_client["client"]
    user = setup_client["user"]
    business_area = setup_client["business_area"]
    list_url = setup_client["list_url"]

    role = RoleFactory(name="Dashboard Viewer", permissions=[Permissions.DASHBOARD_VIEW_COUNTRY.value])
    RoleAssignment.objects.create(user=user, role=role, business_area=business_area)

    response = client.get(list_url)
    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "application/json"


@pytest.mark.django_db(databases=["default"])
@patch("hope.apps.dashboard.views.generate_dash_report_task.delay")
def test_create_or_update_dash_report_task_triggered(
    mock_task_delay: Mock, setup_client: Dict[str, Optional[object]]
) -> None:
    """
    Test that the DashReport generation task is successfully triggered for a superuser.
    """
    user = setup_client["user"]
    client = setup_client["client"]
    generate_report_url = setup_client["generate_report_url"]

    user.is_superuser = True
    user.save()

    response = client.post(generate_report_url)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data["detail"] == "DashReport generation task has been triggered."
    mock_task_delay.assert_called_once_with(setup_client["business_area"].slug)


@pytest.mark.django_db(databases=["default"])
def test_create_or_update_dash_report_permission_denied(setup_client: Dict[str, Optional[object]]) -> None:
    """
    Test that the report creation or update is denied to users without permissions.
    """
    client = setup_client["client"]
    generate_report_url = setup_client["generate_report_url"]
    response = client.post(generate_report_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db(databases=["default"])
@patch("hope.apps.dashboard.views.generate_dash_report_task.delay")
def test_create_or_update_dash_report_business_area_not_found(mock_task_delay: Mock, api_client: Callable) -> None:
    """
    Test that a 404 is returned if the business area does not exist.
    """
    user = UserFactory(is_superuser=True)
    client = api_client(user)
    non_existent_slug = "non-existent-area"
    url = reverse("api:generate-dashreport", args=[non_existent_slug])

    response = client.post(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert str(response.data["detail"]) == "No BusinessArea matches the given query."
    mock_task_delay.assert_not_called()


@pytest.mark.django_db(databases=["default"])
@patch("hope.apps.dashboard.views.generate_dash_report_task.delay", side_effect=Exception("Unexpected error"))
def test_create_or_update_dash_report_internal_server_error(
    mock_task_delay: Mock, setup_client: Dict[str, Optional[object]]
) -> None:
    """
    Test that a 500 response is returned when an unexpected error occurs.
    """
    user = setup_client["user"]
    client = setup_client["client"]
    generate_report_url = setup_client["generate_report_url"]

    user.is_superuser = True
    user.save()

    response = client.post(generate_report_url)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data["detail"] == "Unexpected error"
    mock_task_delay.assert_called_once_with(setup_client["business_area"].slug)


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_report_view_context_with_permission(afghanistan: BusinessAreaFactory, rf: RequestFactory) -> None:
    """
    Test that the DashboardReportView includes the correct context data when the user has permission.
    """
    user = UserFactory()
    role = RoleFactory(name="Dashboard Viewer", permissions=[Permissions.DASHBOARD_VIEW_COUNTRY.value])
    RoleAssignment.objects.create(user=user, role=role, business_area=afghanistan)
    request = rf.get(reverse("api:dashboard", kwargs={"business_area_slug": afghanistan.slug}))
    request.user = user
    view = DashboardReportView()
    view.request = request
    context = view.get_context_data(business_area_slug=afghanistan.slug)
    assert context["business_area_slug"] == afghanistan.slug
    assert context["household_data_url"] == reverse("api:household-data", args=[afghanistan.slug])


def test_dashboard_report_view_context_without_permission(afghanistan: Callable, rf: RequestFactory) -> None:
    """
    Test that the DashboardReportView returns an error message in the context when the user lacks permission.
    """
    user = UserFactory()
    request = rf.get(reverse("api:dashboard", kwargs={"business_area_slug": afghanistan.slug}))
    request.user = user
    view = DashboardReportView()
    view.request = request
    context = view.get_context_data(business_area_slug=afghanistan.slug)
    assert not context["has_permission"]
    assert context["error_message"] == "You do not have permission to view this dashboard."


@pytest.mark.parametrize(
    "business_area_slug, expected_url_key, expected_status, permission_granted",
    [
        ("afghanistan", "list_url", status.HTTP_403_FORBIDDEN, False),
        ("afghanistan", "list_url", status.HTTP_200_OK, True),
    ],
)
def test_dashboard_data_view_permissions(
    business_area_slug: str,
    expected_url_key: str,
    expected_status: int,
    permission_granted: bool,
    setup_client: Dict[str, Optional[object]],
    populate_dashboard_cache: Callable,
) -> None:
    """
    Test permissions for accessing dashboard data, including global and specific business area dashboards.
    """
    client = setup_client["client"]
    user = setup_client["user"]
    business_area = setup_client["business_area"]
    url = setup_client[expected_url_key]

    if permission_granted:
        role = RoleFactory(name="Dashboard Viewer", permissions=[Permissions.DASHBOARD_VIEW_COUNTRY.value])
        assigned_area = "global" if business_area_slug == "global" else business_area
        RoleAssignment.objects.create(user=user, role=role, business_area=assigned_area)

    _ = populate_dashboard_cache(business_area)

    response = client.get(url)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response["Content-Type"] == "application/json"


@pytest.mark.django_db(transaction=True, databases=["default", "read_only"])
def test_dashboard_data_view_global_slug_cache_miss(
    setup_client: Dict[str, Optional[object]],
    populate_dashboard_cache: Callable,
) -> None:
    """Test DashboardDataView with 'global' slug and cache miss."""
    client = setup_client["client"]
    user = setup_client["user"]
    global_url = setup_client["global_url"]

    populate_dashboard_cache(setup_client["business_area"])
    user.is_superuser = True
    user.save()
    client.force_authenticate(user=user)

    cache.delete(DashboardGlobalDataCache.get_cache_key("global"))
    with (
        patch.object(DashboardGlobalDataCache, "get_data", return_value=None) as mock_get_data,
        patch("hope.apps.dashboard.views.generate_dash_report_task.delay") as mock_task_delay,
    ):
        response = client.get(global_url)

        mock_get_data.assert_called_once_with("global")
        mock_task_delay.assert_called_once_with("global")

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "application/json"
    assert response.data == []


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_report_view_global_slug(
    rf: RequestFactory,
) -> None:
    """Test DashboardReportView context and template for 'global' slug."""
    user = UserFactory(is_superuser=True, is_staff=True)
    assert user.is_superuser, "UserFactory did not create a superuser."
    assert user.is_authenticated, "UserFactory user is not authenticated."

    request = rf.get(reverse("api:dashboard", kwargs={"business_area_slug": "global"}))
    request.user = user

    view = DashboardReportView()
    view.setup(request, business_area_slug="global")
    context = view.get_context_data(business_area_slug="global")

    assert view.template_name == "dashboard/global_dashboard.html"
    assert context.get("has_permission") is True, (
        f"Permission denied for global report. User superuser: {request.user.is_superuser},"
        f" User authenticated: {request.user.is_authenticated}. Error: {context.get('error_message')}"
    )
    assert context["business_area_slug"] == "global"
    assert context["household_data_url"] == reverse("api:household-data", args=["global"])


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_report_view_business_area_not_found_http404(rf: RequestFactory) -> None:
    """Test DashboardReportView raises Http404 for a non-existent business_area_slug."""
    user = UserFactory()
    non_existent_slug = "absolutely-does-not-exist"
    BusinessArea.objects.filter(slug=non_existent_slug).delete()

    request = rf.get(reverse("api:dashboard", kwargs={"business_area_slug": non_existent_slug}))
    request.user = user

    view = DashboardReportView()
    view.setup(request, business_area_slug=non_existent_slug)

    with pytest.raises(Http404):
        view.get_context_data(business_area_slug=non_existent_slug)
