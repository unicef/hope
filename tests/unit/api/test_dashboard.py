import contextlib
from typing import Iterator

from rest_framework import status
from rest_framework.reverse import reverse
from tests.unit.api.base import HOPEApiTestCase

from hct_mis_api.api.models import APIToken, Grant
from hct_mis_api.apps.dashboard.factories import BusinessAreaFactory, DashReportFactory


@contextlib.contextmanager
def token_grant_permission(token: APIToken, grant: Grant) -> Iterator:
    old = token.grants
    token.grants += [grant.name]
    token.save()
    yield
    token.grants = old
    token.save()


class DashReportAPITestCase(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = BusinessAreaFactory.create()
        cls.dash_report = DashReportFactory.create(business_area=cls.business_area)

        cls.list_url = reverse("dashboard-report", args=[cls.business_area.slug])

    def test_get_dash_report(self) -> None:
        """Test fetching a dash report for a valid business area with the right permissions."""
        response = self.client.get(self.list_url)
        assert response.status_code == 403

        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.json())
        self.assertIn("households", response.json())

    def test_get_nonexistent_business_area(self) -> None:
        """Test fetching a dash report for a nonexistent business area."""
        url = reverse("dashboard-report", args=["nonexistent-business"])

        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Business area not found.")

    def test_generate_report(self) -> None:
        """Test generating a DashReport for a business area by a superuser."""
        url = reverse("create-update-dash-report", args=[self.business_area.slug])

        with token_grant_permission(self.token, Grant.API_RDI_CREATE):
            response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "DashReport generation task has been triggered.")

    def test_generate_report_permission_denied(self) -> None:
        """Test generating a DashReport by a non-superuser."""
        url = reverse("create-update-dash-report", args=[self.business_area.slug])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.json()["detail"],
            "Only superusers are allowed to create or update DashReports.",
        )

        with token_grant_permission(self.token, Grant.API_RDI_CREATE):
            response = self.client.post(url)
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
