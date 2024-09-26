from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from hct_mis_api.apps.dashboard.factories import BusinessAreaFactory, DashReportFactory


class DashReportAPITestCase(APITestCase):
    def setUp(self) -> None:
        # Create superuser for testing
        self.superuser = User.objects.create_superuser(username="admin", password="admin123")
        self.client.login(username="admin", password="admin123")

        self.business_area = BusinessAreaFactory.create()
        self.dash_report = DashReportFactory.create(business_area=self.business_area)

    def test_get_dash_report(self) -> None:
        """Test fetching a dash report for a valid business area."""

        url = reverse("dashboard-report", args=[self.business_area.slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.json())
        self.assertIn("households", response.json())

    def test_get_nonexistent_business_area(self) -> None:
        """Test fetching a dash report for a nonexistent business area."""

        url = reverse("dashboard-report", args=["nonexistent-business"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Business area not found.")

    def test_generate_report(self) -> None:
        """Test generating a DashReport for a business area by a superuser."""

        url = reverse("create-update-dash-report", args=[self.business_area.slug])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "DashReport generation task has been triggered.")

    def test_generate_report_permission_denied(self) -> None:
        """Test generating a DashReport by a non-superuser."""

        self.client.logout()
        self.client.login(username="user", password="password")

        url = reverse("create-update-dash-report", args=[self.business_area.slug])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Only superusers are allowed to create or update DashReports.")
