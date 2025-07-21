import base64
from unittest.mock import Mock, patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Role, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from tests.extras.test_utils.factories.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.api.views import WebhookDeduplicationView
from tests.unit.api.base import HOPEApiTestCase


class RegistrationDataImportViewSetTest(HOPEApiTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        user_permissions = [
            Permissions.RDI_VIEW_LIST,
        ]
        partner = PartnerFactory(name="UNICEF")
        cls.user = UserFactory(username="Hope_Test_DRF", password="HopePass", partner=partner, is_superuser=True)
        permission_list = [perm.value for perm in user_permissions]
        role, created = Role.objects.update_or_create(name="TestName", defaults={"permissions": permission_list})
        user_role, _ = UserRole.objects.get_or_create(user=cls.user, role=role, business_area=cls.business_area)
        cls.program = ProgramFactory(
            name="Test Program",
            status=Program.ACTIVE,
        )
        cls.str_program_id = str(cls.program.id)
        cls.program_id_base64 = base64.b64encode(f"ProgramNode:{cls.str_program_id}".encode()).decode()
        cls.factory = APIRequestFactory()
        cls.client = APIClient()

    @patch("hct_mis_api.apps.registration_datahub.celery_tasks.deduplication_engine_process.delay")
    def test_run_deduplication(self, mock_deduplication_engine_process: Mock) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:registration-data:registration-data-imports-run-deduplication",
            args=["afghanistan", self.program_id_base64],
        )
        resp = self.client.post(url, {}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {"message": "Deduplication process started"})
        mock_deduplication_engine_process.assert_called_once_with(str(self.program.id))


class WebhookDeduplicationViewTest(HOPEApiTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.program = ProgramFactory(
            name="Test Program",
            status=Program.ACTIVE,
        )
        cls.str_program_id = str(cls.program.id)
        cls.factory = APIRequestFactory()

    @patch("hct_mis_api.apps.registration_datahub.celery_tasks.fetch_biometric_deduplication_results_and_process.delay")
    def test_webhook_deduplication(self, mock_fetch_dedup_results: Mock) -> None:
        url = reverse("api:registration-data:webhook_deduplication", args=["afghanistan", self.str_program_id])
        request = self.factory.get(url)
        view = WebhookDeduplicationView.as_view()
        response = view(request, business_area=self.program.business_area.id, program_id=self.program.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_fetch_dedup_results.assert_called_once_with(self.program.deduplication_set_id)
