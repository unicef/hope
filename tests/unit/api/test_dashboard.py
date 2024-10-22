from typing import Callable, List, Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.dashboard.services import DashboardDataCache

pytestmark = pytest.mark.django_db


class TestDashboardDataView:
    def set_up(self, api_client: Callable, business_area: BusinessAreaFactory) -> None:
        self.user: User = UserFactory(is_superuser=False, is_staff=False)
        self.client: APIClient = api_client(self.user)
        self.business_area: BusinessAreaFactory = business_area
        self.business_area_2: BusinessAreaFactory = BusinessAreaFactory(name="Test Business Area 2")

        DashboardDataCache.refresh_data(self.business_area.slug)

        self.list_url: str = reverse("api:household-data", args=[self.business_area.slug])
        self.generate_report_url: str = reverse("api:generate-dashreport", args=[self.business_area.slug])

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([], status.HTTP_403_FORBIDDEN),
            ([Permissions.DASHBOARD_VIEW_COUNTRY], status.HTTP_200_OK),
        ],
    )
    @pytest.mark.django_db(databases=["default", "read_only"])
    def test_dashboard_data_permission(
        self,
        permissions: List[str],
        expected_status: int,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(self.user, permissions, self.business_area)

        response = self.client.get(self.list_url)
        assert response.status_code == expected_status

    @pytest.mark.django_db(databases=["default", "read_only"])
    def test_get_dash_report_json(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        """
        Test fetching the dashboard report and ensure it contains valid JSON.
        """
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(self.user, [Permissions.DASHBOARD_VIEW_COUNTRY], self.business_area)

        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "application/json"

        report_data: List[Any] = response.json()
        assert isinstance(report_data, list)
        assert "total_households" in report_data
        assert "last_updated" in report_data

    @pytest.mark.django_db(databases=["default", "read_only"])
    def test_get_nonexistent_business_area(self, api_client: Callable, afghanistan: BusinessAreaFactory) -> None:
        """Test fetching a dashboard report for a nonexistent business area."""
        self.set_up(api_client, afghanistan)

        url: str = reverse("api:household-data", args=["nonexistent-business"])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
