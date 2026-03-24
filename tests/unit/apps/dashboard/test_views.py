from typing import Callable
from unittest.mock import Mock, patch

from django.core.cache import cache
from django.db import OperationalError
from django.http import Http404
from django.test import RequestFactory
from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    HouseholdFactory,
    PaymentFactory,
    ProgramFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.dashboard.services import DashboardGlobalDataCache
from hope.apps.dashboard.views import DashboardReportView
from hope.models import BusinessArea, Payment, PaymentPlan, RoleAssignment


@pytest.fixture
def use_default_db_for_dashboard():
    with (
        patch("hope.apps.dashboard.services.settings.DASHBOARD_DB", "default"),
        patch("hope.apps.dashboard.celery_tasks.settings.DASHBOARD_DB", "default"),
    ):
        yield


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("use_default_db_for_dashboard"),
]


@pytest.fixture
def afghanistan(db):
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        slug="afghanistan",
        has_data_sharing_agreement=True,
        kobo_token="XXX",
        active=True,
    )


@pytest.fixture
def global_business_area(db):
    return BusinessAreaFactory(
        slug="global",
        name="Global",
        code="GLOBAL",
        long_name="Global Business Area",
        region_code="GLOBAL",
        region_name="GLOBAL",
        has_data_sharing_agreement=True,
    )


@pytest.fixture
def area_kabul(db):
    area_type = AreaTypeFactory(name="Province", area_level=1)
    return AreaFactory(name="Kabul", area_type=area_type)


@pytest.fixture
def populate_dashboard_cache(area_kabul):
    def _populate(ba, household_extra_args=None):
        program = ProgramFactory(business_area=ba)
        household = HouseholdFactory(
            business_area=ba,
            program=program,
            size=5,
            children_count=2,
            female_age_group_0_5_disabled_count=1,
            female_age_group_6_11_disabled_count=1,
            male_age_group_60_disabled_count=1,
            admin1=area_kabul,
            **(household_extra_args or {}),
        )
        payment_statuses = [
            Payment.STATUS_SUCCESS,
            Payment.STATUS_DISTRIBUTION_SUCCESS,
            Payment.STATUS_DISTRIBUTION_PARTIAL,
            Payment.STATUS_PENDING,
            Payment.STATUS_SUCCESS,
        ]
        for payment_status in payment_statuses:
            PaymentFactory(
                household=household,
                program=program,
                business_area=ba,
                parent__status=PaymentPlan.Status.ACCEPTED,
                status=payment_status,
            )
        return household

    return _populate


@pytest.fixture
def user(db):
    return UserFactory(is_superuser=False, is_staff=False)


@pytest.fixture
def superuser(db):
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture
def dashboard_viewer_role(db):
    return RoleFactory(
        name="Dashboard Viewer",
        permissions=[Permissions.DASHBOARD_VIEW_COUNTRY.value],
    )


@pytest.fixture
def api_client():
    def _api_client(user_account=None):
        if not user_account:
            user_account = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user_account)
        return client

    return _api_client


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_data_view_permission_denied(
    api_client: Callable, user: UserFactory, afghanistan: BusinessArea
) -> None:
    """
    Test that access to the dashboard data is denied for users without permissions.
    """
    client = api_client(user)
    list_url = reverse("api:household-data", args=[afghanistan.slug])
    response = client.get(list_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_data_view_access_granted(
    api_client: Callable,
    user: UserFactory,
    afghanistan: BusinessArea,
    dashboard_viewer_role: RoleFactory,
    populate_dashboard_cache: Callable,
) -> None:
    """
    Test that access to the dashboard data is granted for users with permissions.
    """
    client = api_client(user)
    list_url = reverse("api:household-data", args=[afghanistan.slug])

    RoleAssignment.objects.create(user=user, role=dashboard_viewer_role, business_area=afghanistan)

    response = client.get(list_url)
    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "application/json"


@pytest.mark.django_db(databases=["default"])
@patch("hope.apps.dashboard.views.generate_dash_report_task.delay")
def test_create_or_update_dash_report_task_triggered_for_superuser(
    mock_task_delay: Mock, api_client: Callable, superuser: UserFactory, afghanistan: BusinessArea
) -> None:
    """
    Test that the DashReport generation task is successfully triggered for a superuser.
    """
    client = api_client(superuser)
    generate_report_url = reverse("api:generate-dashreport", args=[afghanistan.slug])

    response = client.post(generate_report_url)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data["detail"] == "DashReport generation task has been triggered."
    mock_task_delay.assert_called_once_with(afghanistan.slug)


@pytest.mark.django_db(databases=["default"])
@patch("hope.apps.dashboard.views.generate_dash_report_task.delay")
def test_create_or_update_dash_report_task_triggered_with_permission(
    mock_task_delay: Mock,
    api_client: Callable,
    user: UserFactory,
    afghanistan: BusinessArea,
    dashboard_viewer_role: RoleFactory,
) -> None:
    """
    Test that the DashReport generation task is successfully triggered for a user with permission.
    """
    client = api_client(user)
    generate_report_url = reverse("api:generate-dashreport", args=[afghanistan.slug])

    RoleAssignment.objects.create(user=user, role=dashboard_viewer_role, business_area=afghanistan)

    response = client.post(generate_report_url)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data["detail"] == "DashReport generation task has been triggered."
    mock_task_delay.assert_called_once_with(afghanistan.slug)


@pytest.mark.django_db(databases=["default"])
def test_create_or_update_dash_report_permission_denied(
    api_client: Callable, user: UserFactory, afghanistan: BusinessArea
) -> None:
    """
    Test that the report creation or update is denied to users without permissions.
    """
    client = api_client(user)
    generate_report_url = reverse("api:generate-dashreport", args=[afghanistan.slug])
    response = client.post(generate_report_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db(databases=["default"])
@patch("hope.apps.dashboard.views.generate_dash_report_task.delay")
def test_create_or_update_dash_report_business_area_not_found(
    mock_task_delay: Mock, api_client: Callable, superuser: UserFactory
) -> None:
    """
    Test that a 404 is returned if the business area does not exist.
    """
    client = api_client(superuser)
    non_existent_slug = "non-existent-area"
    url = reverse("api:generate-dashreport", args=[non_existent_slug])

    response = client.post(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert str(response.data["detail"]) == "No BusinessArea matches the given query."
    mock_task_delay.assert_not_called()


@pytest.mark.django_db(databases=["default"])
@patch(
    "hope.apps.dashboard.views.generate_dash_report_task.delay",
    side_effect=OperationalError("Unexpected error"),
)
def test_create_or_update_dash_report_internal_server_error(
    mock_task_delay: Mock, api_client: Callable, superuser: UserFactory, afghanistan: BusinessArea
) -> None:
    """Test that a 500 response is returned when an unexpected error occurs."""
    client = api_client(superuser)
    generate_report_url = reverse("api:generate-dashreport", args=[afghanistan.slug])

    response = client.post(generate_report_url)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data["detail"] == "Unexpected error"
    mock_task_delay.assert_called_once_with(afghanistan.slug)


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_report_view_context_with_permission(
    afghanistan: BusinessArea, rf: RequestFactory, user: UserFactory, dashboard_viewer_role: RoleFactory
) -> None:
    """
    Test that the DashboardReportView includes the correct context data when the user has permission.
    """
    RoleAssignment.objects.create(user=user, role=dashboard_viewer_role, business_area=afghanistan)
    request = rf.get(reverse("api:dashboard", kwargs={"business_area_slug": afghanistan.slug}))
    request.user = user
    view = DashboardReportView()
    view.request = request
    context = view.get_context_data(business_area_slug=afghanistan.slug)
    assert context["business_area_slug"] == afghanistan.slug
    assert context["household_data_url"] == reverse("api:household-data", args=[afghanistan.slug])


def test_dashboard_report_view_context_without_permission(
    afghanistan: BusinessArea, rf: RequestFactory, user: UserFactory
) -> None:
    """
    Test that the DashboardReportView returns an error message in the context when the user lacks permission.
    """
    request = rf.get(reverse("api:dashboard", kwargs={"business_area_slug": afghanistan.slug}))
    request.user = user
    view = DashboardReportView()
    view.request = request
    context = view.get_context_data(business_area_slug=afghanistan.slug)
    assert not context["has_permission"]
    assert context["error_message"] == "You do not have permission to view this dashboard."


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_data_view_permission_denied_afghanistan(
    api_client: Callable,
    user: UserFactory,
    afghanistan: BusinessArea,
    populate_dashboard_cache: Callable,
) -> None:
    """
    Test that access to the Afghanistan dashboard is denied for users without permissions.
    """
    client = api_client(user)
    list_url = reverse("api:household-data", args=[afghanistan.slug])
    populate_dashboard_cache(afghanistan)

    response = client.get(list_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_data_view_access_granted_afghanistan(
    api_client: Callable,
    user: UserFactory,
    afghanistan: BusinessArea,
    dashboard_viewer_role: RoleFactory,
    populate_dashboard_cache: Callable,
) -> None:
    """
    Test that access to the Afghanistan dashboard is granted for users with permissions.
    """
    client = api_client(user)
    list_url = reverse("api:household-data", args=[afghanistan.slug])
    RoleAssignment.objects.create(user=user, role=dashboard_viewer_role, business_area=afghanistan)
    populate_dashboard_cache(afghanistan)

    response = client.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "application/json"


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_data_view_permission_denied_global(
    api_client: Callable,
    user: UserFactory,
    afghanistan: BusinessArea,
    global_business_area: BusinessArea,
    populate_dashboard_cache: Callable,
) -> None:
    """
    Test that access to the global dashboard is denied for users without permissions.
    """
    client = api_client(user)
    global_url = reverse("api:household-data", args=["global"])
    populate_dashboard_cache(afghanistan)

    response = client.get(global_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db(databases=["default", "read_only"])
def test_dashboard_data_view_access_granted_global(
    api_client: Callable,
    user: UserFactory,
    afghanistan: BusinessArea,
    global_business_area: BusinessArea,
    dashboard_viewer_role: RoleFactory,
    populate_dashboard_cache: Callable,
) -> None:
    """
    Test that access to the global dashboard is granted for users with permissions.
    """
    client = api_client(user)
    global_url = reverse("api:household-data", args=["global"])
    RoleAssignment.objects.create(user=user, role=dashboard_viewer_role, business_area=global_business_area)
    populate_dashboard_cache(afghanistan)

    response = client.get(global_url)

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "application/json"


def test_dashboard_data_view_global_slug_cache_miss(
    api_client: Callable,
    user: UserFactory,
    afghanistan: BusinessArea,
    global_business_area: BusinessArea,
    dashboard_viewer_role: RoleFactory,
    populate_dashboard_cache: Callable,
) -> None:
    """Test DashboardDataView with 'global' slug and cache miss."""
    client = api_client(user)
    global_url = reverse("api:household-data", args=["global"])

    RoleAssignment.objects.create(user=user, role=dashboard_viewer_role, business_area=global_business_area)

    populate_dashboard_cache(afghanistan)

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
    user: UserFactory,
    global_business_area: BusinessArea,
    dashboard_viewer_role: RoleFactory,
) -> None:
    """Test DashboardReportView context and template for 'global' slug."""
    RoleAssignment.objects.create(user=user, role=dashboard_viewer_role, business_area=global_business_area)

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
def test_dashboard_report_view_business_area_not_found_http404(rf: RequestFactory, user: UserFactory) -> None:
    """Test DashboardReportView raises Http404 for a non-existent business_area_slug."""
    non_existent_slug = "absolutely-does-not-exist"
    BusinessArea.objects.filter(slug=non_existent_slug).delete()

    request = rf.get(reverse("api:dashboard", kwargs={"business_area_slug": non_existent_slug}))
    request.user = user

    view = DashboardReportView()
    view.setup(request, business_area_slug=non_existent_slug)

    with pytest.raises(Http404):
        view.get_context_data(business_area_slug=non_existent_slug)
