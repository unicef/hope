import json

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status

from hct_mis_api.api.models import APIToken, Grant
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, RoleFactory, UserFactory, UserRoleFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.dashboard.services import DashboardDataCache


def test_get_dash_report_json(api_client, business_area):
    """
    Test fetching the dashboard report and ensure it contains valid JSON when fetched via the API.
    """
    user = UserFactory(is_superuser=False, is_staff=False)
    api_client.force_login(user)

    url = reverse("api:household-data", args=[business_area.slug])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    role = RoleFactory(name="Dashboard Viewer", subsystem="API", permissions=[Permissions.DASHBOARD_VIEW_COUNTRY.name])
    UserRoleFactory(user=user, role=role, business_area=business_area)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "application/json"

    report_data = response.json()
    assert isinstance(report_data, dict)
    assert "total_households" in report_data
    assert "last_updated" in report_data


def test_get_dash_report_with_valid_permissions(api_client, business_area):
    """Test fetching a dashboard report with valid permissions."""
    user = UserFactory(is_superuser=False, is_staff=False)
    api_client.force_login(user)

    role = RoleFactory(name="Dashboard Viewer", subsystem="API", permissions=[Permissions.DASHBOARD_VIEW_COUNTRY.name])
    UserRoleFactory(user=user, role=role, business_area=business_area)

    url = reverse("api:household-data", args=[business_area.slug])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_get_dash_report_without_permissions(api_client, business_area):
    """Test fetching a dashboard report without permissions returns 403."""
    user = UserFactory(is_superuser=False, is_staff=False)
    api_client.force_login(user)

    url = reverse("api:household-data", args=[business_area.slug])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_nonexistent_business_area(api_client):
    """Test fetching a dashboard report for a nonexistent business area."""
    user = UserFactory(is_superuser=False, is_staff=False)
    api_client.force_login(user)

    url = reverse("api:household-data", args=["nonexistent-business"])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_generate_report_permission_denied(api_client, business_area):
    """Test generating a DashReport as a non-superuser returns 403."""
    user = UserFactory(is_superuser=False, is_staff=False)
    api_client.force_login(user)

    url = reverse("api:generate-dashreport", args=[business_area.slug])
    response = api_client.post(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == (
        "Only superusers or users with the correct permissions can create or update DashReports."
    )


def test_generate_report_as_superuser(api_client, business_area):
    """Test generating a DashReport as a superuser works."""
    user = UserFactory(is_superuser=True, is_staff=True)
    api_client.force_login(user)

    url = reverse("api:generate-dashreport", args=[business_area.slug])
    response = api_client.post(url)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "detail" in response.json()
    assert response.json()["detail"] == "DashReport generation task has been triggered."


def test_access_other_business_area_fails(api_client, business_area, other_business_area):
    """Test accessing a DashReport from a different business area fails."""
    user = UserFactory(is_superuser=False, is_staff=False)
    api_client.force_login(user)

    token = APIToken.objects.create(user=user)
    token.grants += [Grant.API_READ_ONLY.name]
    token.save()
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    url = reverse("api:household-data", args=[other_business_area.slug])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "You do not have permission to view this dashboard."
