from unittest import skip

from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import MigrationStatus


class TestMaintenancePage(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
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

        assert MigrationStatus.objects.count() == 0
        for endpoint in not_blocked_endpoionts:
            assert_ok(endpoint)
        for endpoint in blocked_enpoints:
            assert_ok(endpoint)

        MigrationStatus.objects.create(is_running=True)
        for endpoint in not_blocked_endpoionts:
            assert_ok(endpoint)
        for endpoint in blocked_enpoints:
            assert_forbidden(endpoint)
