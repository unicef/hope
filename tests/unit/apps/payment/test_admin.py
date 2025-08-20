import os
from typing import Any
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    PaymentFactory,
    PaymentPlanFactory,
)

from hope.admin.payment_plan import (
    can_regenerate_export_file_per_fsp,
    can_sync_with_payment_gateway,
)
from hope.apps.payment.models import FinancialServiceProvider, PaymentPlan


@pytest.fixture(autouse=True)
def mock_payment_gateway_env_vars() -> None:
    with patch.dict(
        os.environ,
        {"PAYMENT_GATEWAY_API_KEY": "TEST", "PAYMENT_GATEWAY_API_URL": "TEST"},
    ):
        yield


class SyncWithPaymentGatewayTest(TestCase):
    def setUp(self: Any) -> None:
        self.business_area = create_afghanistan()
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(username="root", email="root@root.com", password="password")
        self.client.login(username=self.admin_user.username, password="password")
        self.financial_service_provider = FinancialServiceProviderFactory(
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
            payment_gateway_id="test123",
        )
        self.dm = DeliveryMechanismFactory()
        self.payment_plan = PaymentPlanFactory(
            name="Test Plan",
            status=PaymentPlan.Status.ACCEPTED,
            financial_service_provider=self.financial_service_provider,
            delivery_mechanism=self.dm,
        )
        self.payment = PaymentFactory(
            parent=self.payment_plan,
        )

    @patch("hope.apps.payment.services.payment_gateway.PaymentGatewayService.sync_payment_plan")
    @patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
    def test_payment_plan_post_sync_with_payment_gateway(self: Any, mock_perm: Any, mock_sync: Any) -> None:
        url = reverse(
            "admin:payment_paymentplan_sync_with_payment_gateway",
            args=[self.payment_plan.pk],
        )
        response = self.client.post(url)

        mock_sync.assert_called_once_with(self.payment_plan)
        assert response.status_code == 302
        assert reverse("admin:payment_paymentplan_change", args=[self.payment_plan.pk]) in response["Location"]

    @patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
    def test_payment_plan_get_sync_with_payment_gateway_confirmation(self: Any, mock_perm: Any) -> None:
        url = reverse(
            "admin:payment_paymentplan_sync_with_payment_gateway",
            args=[self.payment_plan.pk],
        )
        response = self.client.get(url)

        assert response.status_code == 200
        self.assertContains(response, "Do you confirm to Sync with Payment Gateway?")

    @patch("hope.apps.payment.services.payment_gateway.PaymentGatewayService.sync_record")
    @patch("hope.admin.payment_plan.has_payment_pg_sync_permission", return_value=True)
    def test_payment_post_sync_with_payment_gateway(self: Any, mock_perm: Any, mock_sync: Any) -> None:
        url = reverse("admin:payment_payment_sync_with_payment_gateway", args=[self.payment.pk])
        response = self.client.post(url)

        mock_sync.assert_called_once_with(self.payment)
        assert response.status_code == 302
        assert reverse("admin:payment_payment_change", args=[self.payment.pk]) in response["Location"]

    @patch("hope.admin.payment_plan.has_payment_pg_sync_permission", return_value=True)
    def test_payment_get_sync_with_payment_gateway_confirmation(self: Any, mock_perm: Any) -> None:
        url = reverse("admin:payment_payment_sync_with_payment_gateway", args=[self.payment.pk])
        response = self.client.get(url)

        assert response.status_code == 200
        self.assertContains(response, "Do you confirm to Sync with Payment Gateway?")

    def test_payment_plan_related_configs_button(self: Any) -> None:
        url = reverse("admin:payment_paymentplan_related_configs", args=[self.payment_plan.pk])
        response = self.client.get(url)
        assert response.status_code == 302
        assert reverse("admin:payment_deliverymechanismconfig_changelist") in response["Location"]

    @patch(
        "hope.apps.payment.services.payment_gateway.PaymentGatewayService.add_missing_records_to_payment_instructions"
    )
    @patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
    def test_payment_post_sync_missing_records_with_payment_gateway(self: Any, mock_perm: Any, mock_sync: Any) -> None:
        url = reverse(
            "admin:payment_paymentplan_sync_missing_records_with_payment_gateway",
            args=[self.payment_plan.pk],
        )
        response = self.client.post(url)

        mock_sync.assert_called_once_with(self.payment_plan)
        assert response.status_code == 302
        assert reverse("admin:payment_paymentplan_change", args=[self.payment_plan.pk]) in response["Location"]

    @patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
    def test_payment_get_sync_missing_records_with_payment_gateway(self: Any, mock_perm: Any) -> None:
        url = reverse(
            "admin:payment_paymentplan_sync_missing_records_with_payment_gateway",
            args=[self.payment_plan.pk],
        )
        response = self.client.get(url)

        assert response.status_code == 200
        self.assertContains(response, "Do you confirm to Sync with Payment Gateway missing Records?")

    @patch("hope.apps.payment.admin.has_payment_plan_export_per_fsp_permission", return_value=True)
    def test_get_regenerate_export_xlsx_form(self, mock_perm: Any) -> None:
        url = reverse("admin:payment_paymentplan_regenerate_export_xlsx", args=[self.payment_plan.pk])
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertContains(response, "Select a template if you want the export to include the FSP Auth Code")
        assert "form" in response.context

    @patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.export_xlsx_per_fsp")
    @patch("hope.apps.payment.admin.has_payment_plan_export_per_fsp_permission", return_value=True)
    def test_post_regenerate_export_xlsx_without_template(self, mock_perm: Any, mock_export: Any) -> None:
        url = reverse("admin:payment_paymentplan_regenerate_export_xlsx", args=[self.payment_plan.pk])
        response = self.client.post(url, {"template": ""})  # no template selected

        mock_export.assert_called_once_with(self.admin_user.pk, None)
        assert response.status_code == 302
        assert reverse("admin:payment_paymentplan_change", args=[self.payment_plan.pk]) in response["Location"]

    @patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.export_xlsx_per_fsp")
    @patch("hope.apps.payment.admin.has_payment_plan_export_per_fsp_permission", return_value=True)
    def test_post_regenerate_export_xlsx_with_template(self, mock_perm: Any, mock_export: Any) -> None:
        self.client.force_login(self.admin_user)
        template = FinancialServiceProviderXlsxTemplateFactory(name="Test Template AAA")
        fsp = FinancialServiceProviderFactory()
        fsp.allowed_business_areas.add(self.payment_plan.business_area)
        fsp.xlsx_templates.add(template)
        url = reverse("admin:payment_paymentplan_regenerate_export_xlsx", args=[self.payment_plan.pk])
        response = self.client.post(url, {"template": template.id})

        mock_export.assert_called_once_with(self.admin_user.pk, str(template.id))
        assert response.status_code == 302
        assert reverse("admin:payment_paymentplan_change", args=[self.payment_plan.pk]) in response["Location"]

    def test_can_sync_with_payment_gateway(self) -> None:
        assert not can_sync_with_payment_gateway(self.payment_plan)

    def test_can_regenerate_export_file_per_fsp(self) -> None:
        assert not can_regenerate_export_file_per_fsp(self.payment_plan)
