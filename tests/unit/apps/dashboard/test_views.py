from typing import Callable, Dict, List, Optional

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)
from hct_mis_api.apps.account.models import UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import BusinessArea

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
    generate_report_url = reverse("api:generate-dashreport", args=[afghanistan.slug])

    return {
        "client": client,
        "user": user,
        "business_area": afghanistan,
        "list_url": list_url,
        "generate_report_url": generate_report_url,
    }


@pytest.mark.parametrize(
    "permissions, expected_status",
    [
        ([], status.HTTP_403_FORBIDDEN),
        ([Permissions.DASHBOARD_VIEW_COUNTRY], status.HTTP_200_OK),
    ],
)
def test_dashboard_data_permission(
    permissions: List[Permissions],
    expected_status: int,
    setup_client: Dict[str, Optional[object]],
    populate_dashboard_cache: Callable,
) -> None:
    client = setup_client["client"]
    user = setup_client["user"]
    business_area = setup_client["business_area"]
    list_url = setup_client["list_url"]

    if permissions:
        role = RoleFactory(name="Test Role", permissions=permissions)
        UserRole.objects.create(user=user, role=role, business_area=business_area)

    response = client.get(list_url)
    assert response.status_code == expected_status


def test_get_dash_report_json(
    setup_client: Dict[str, Optional[object]],
    populate_dashboard_cache: Callable,
) -> None:
    """
    Test fetching the dashboard report and ensure it contains valid JSON.
    """
    client = setup_client["client"]
    user = setup_client["user"]
    business_area = setup_client["business_area"]
    list_url = setup_client["list_url"]
    role = RoleFactory(name="Dashboard Viewer", permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    UserRole.objects.create(user=user, role=role, business_area=business_area)

    response = client.get(list_url)
    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "application/json"

    report_data = response.json()
    if isinstance(report_data, list) and report_data:
        assert "first_registration_date" in report_data[0]
        assert "admin1" in report_data[0]
        assert "admin2" in report_data[0]
        assert "payments" in report_data[0]


def test_get_nonexistent_business_area(api_client: Callable) -> None:
    user = UserFactory(is_superuser=False, is_staff=False)
    user.user_permissions.clear()
    client = api_client(user)
    url = reverse("api:household-data", args=["nonexistent-business"])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.fixture
def setup_client_with_permissions(api_client: Callable, afghanistan: BusinessArea) -> Dict[str, Optional[object]]:
    """
    Setup client and permissions for DashboardReportView testing.
    """
    user = UserFactory()
    client = api_client(user)
    return {"client": client, "user": user, "business_area": afghanistan}


def test_dashboard_template_view_permission(setup_client_with_permissions: Dict[str, Optional[object]]) -> None:
    """
    Test that users with the correct permissions can view the dashboard.
    """
    setup = setup_client_with_permissions
    client = setup["client"]
    user = setup["user"]
    business_area = setup["business_area"]

    client.force_login(user)

    role = RoleFactory(name="Dashboard Viewer", permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    UserRole.objects.get_or_create(user=user, role=role, business_area=business_area)
    url = reverse("api:dashboard", kwargs={"business_area_slug": business_area.slug})
    response = client.get(url, follow=True)
    assert (
        response.status_code == status.HTTP_200_OK
    ), f"Unexpected status code: {response.status_code}, Content: {response.content}"
    assert hasattr(response, "template_name"), f"Expected template not rendered. Response: {response.content}"
    assert "dashboard/dashboard.html" in response.template_name
