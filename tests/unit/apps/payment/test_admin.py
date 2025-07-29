import os
from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import pytest
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
)

from hct_mis_api.apps.payment.models import FinancialServiceProvider, PaymentPlan


@pytest.fixture(autouse=True)
def mock_payment_gateway_env_vars() -> None:
    with patch.dict(os.environ, {"PAYMENT_GATEWAY_API_KEY": "TEST", "PAYMENT_GATEWAY_API_URL": "TEST"}):
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

    @patch("hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayService.sync_payment_plan")
    @patch("hct_mis_api.admin.payment_admin_payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
    def test_payment_plan_post_sync_with_payment_gateway(self: Any, mock_perm: Any, mock_sync: Any) -> None:
        url = reverse("admin:payment_paymentplan_sync_with_payment_gateway", args=[self.payment_plan.pk])
        response = self.client.post(url)

        mock_sync.assert_called_once_with(self.payment_plan)
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("admin:payment_paymentplan_change", args=[self.payment_plan.pk]),
            response["Location"],
        )

    @patch("hct_mis_api.admin.payment_admin_payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
    def test_payment_plan_get_sync_with_payment_gateway_confirmation(self: Any, mock_perm: Any) -> None:
        url = reverse("admin:payment_paymentplan_sync_with_payment_gateway", args=[self.payment_plan.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you confirm to Sync with Payment Gateway?")

    @patch("hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayService.sync_record")
    @patch("hct_mis_api.admin.payment_admin_payment_plan.has_payment_pg_sync_permission", return_value=True)
    def test_payment_post_sync_with_payment_gateway(self: Any, mock_perm: Any, mock_sync: Any) -> None:
        url = reverse("admin:payment_payment_sync_with_payment_gateway", args=[self.payment.pk])
        response = self.client.post(url)

        mock_sync.assert_called_once_with(self.payment)
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("admin:payment_payment_change", args=[self.payment.pk]),
            response["Location"],
        )

    @patch("hct_mis_api.admin.payment_admin_payment_plan.has_payment_pg_sync_permission", return_value=True)
    def test_payment_get_sync_with_payment_gateway_confirmation(self: Any, mock_perm: Any) -> None:
        url = reverse("admin:payment_payment_sync_with_payment_gateway", args=[self.payment.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you confirm to Sync with Payment Gateway?")

    def test_payment_plan_related_configs_button(self: Any) -> None:
        url = reverse("admin:payment_paymentplan_related_configs", args=[self.payment_plan.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("admin:payment_deliverymechanismconfig_changelist"),
            response["Location"],
        )
