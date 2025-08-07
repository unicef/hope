from unittest import skip

from extras.test_utils.factories.account import UserFactory
from rest_framework.test import APIClient

from hope.apps.core.base_test_case import APITestCase


class TestMaintenancePage(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()
        cls.api_client = APIClient()
        cls.api_client.force_authenticate(user=cls.user)

    @skip("Because not use DisableTrafficDuringMigrationsMiddleware for now")
    def test_blocking_traffic_during_maintenance(self) -> None:
        api_client = APIClient()

        def assert_ok(endpoint: str) -> None:
            response = api_client.get(endpoint)
            assert 200 <= response.status_code < 400

        def assert_forbidden(endpoint: str) -> None:
            response = api_client.get(endpoint)
            assert response.status_code == 403

        not_blocked_endpoionts = [
            "/api/unicorn",
            "/_health",
            "/api/_health",
        ]
        blocked_enpoints = [
            "/",
        ]

        for endpoint in not_blocked_endpoionts:
            assert_ok(endpoint)
        for endpoint in blocked_enpoints:
            assert_ok(endpoint)

        for endpoint in not_blocked_endpoionts:
            assert_ok(endpoint)
        for endpoint in blocked_enpoints:
            assert_forbidden(endpoint)
