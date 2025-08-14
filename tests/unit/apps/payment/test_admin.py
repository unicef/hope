import os
from typing import Any
from unittest.mock import patch

from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import pytest
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    PaymentFactory,
    PaymentPlanFactory,
)

from hct_mis_api.apps.payment.admin import (
    ArrayFieldWidget,
    CommaSeparatedArrayField,
    can_regenerate_export_file_per_fsp,
    can_sync_with_payment_gateway,
)
from hct_mis_api.apps.payment.models import FinancialServiceProvider, PaymentPlan


@pytest.fixture(autouse=True)
def mock_payment_gateway_env_vars() -> None:
    with patch.dict(os.environ, {"PAYMENT_GATEWAY_API_KEY": "TEST", "PAYMENT_GATEWAY_API_URL": "TEST"}):
        yield


class ArrayFieldWidgetTests(TestCase):
    def setUp(self) -> None:
        self.widget = ArrayFieldWidget()

    def test_format_value_none(self) -> None:
        self.assertEqual(self.widget.format_value(None), "")

    def test_format_value_list(self) -> None:
        self.assertEqual(self.widget.format_value(["apple", "banana", "cherry"]), "apple\nbanana\ncherry")

    def test_format_value_string(self) -> None:
        self.assertEqual(self.widget.format_value("test"), "test")

    def test_value_from_datadict_empty(self) -> None:
        self.assertEqual(self.widget.value_from_datadict({}, {}, "field_name"), [])

    def test_value_from_datadict_list(self) -> None:
        data = {"field_name": "apple\n  banana  \ncherry"}
        self.assertEqual(self.widget.value_from_datadict(data, {}, "field_name"), ["apple", "banana", "cherry"])


class CommaSeparatedArrayFieldTests(TestCase):
    def setUp(self) -> None:
        self.field = CommaSeparatedArrayField()

    def test_prepare_value_none(self) -> None:
        self.assertEqual(self.field.prepare_value(None), "")

    def test_prepare_value_list(self) -> None:
        self.assertEqual(self.field.prepare_value(["apple", "banana", "cherry"]), "apple\nbanana\ncherry")

    def test_to_python_empty(self) -> None:
        self.assertEqual(self.field.to_python(""), [])

    def test_to_python_list(self) -> None:
        self.assertEqual(self.field.to_python(["apple", "banana"]), ["apple", "banana"])

    def test_to_python_string(self) -> None:
        self.assertEqual(self.field.to_python("apple\nbanana\ncherry"), ["apple", "banana", "cherry"])

    def test_validate_valid(self) -> None:
        try:
            self.field.validate(["apple", "banana"])
        except forms.ValidationError:
            self.fail("validate() raised ValidationError unexpectedly!")


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
    @patch("hct_mis_api.apps.payment.admin.has_payment_plan_pg_sync_permission", return_value=True)
    def test_payment_plan_post_sync_with_payment_gateway(self: Any, mock_perm: Any, mock_sync: Any) -> None:
        url = reverse("admin:payment_paymentplan_sync_with_payment_gateway", args=[self.payment_plan.pk])
        response = self.client.post(url)

        mock_sync.assert_called_once_with(self.payment_plan)
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("admin:payment_paymentplan_change", args=[self.payment_plan.pk]),
            response["Location"],
        )

    @patch("hct_mis_api.apps.payment.admin.has_payment_plan_pg_sync_permission", return_value=True)
    def test_payment_plan_get_sync_with_payment_gateway_confirmation(self: Any, mock_perm: Any) -> None:
        url = reverse("admin:payment_paymentplan_sync_with_payment_gateway", args=[self.payment_plan.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you confirm to Sync with Payment Gateway?")

    @patch("hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayService.sync_record")
    @patch("hct_mis_api.apps.payment.admin.has_payment_pg_sync_permission", return_value=True)
    def test_payment_post_sync_with_payment_gateway(self: Any, mock_perm: Any, mock_sync: Any) -> None:
        url = reverse("admin:payment_payment_sync_with_payment_gateway", args=[self.payment.pk])
        response = self.client.post(url)

        mock_sync.assert_called_once_with(self.payment)
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("admin:payment_payment_change", args=[self.payment.pk]),
            response["Location"],
        )

    @patch("hct_mis_api.apps.payment.admin.has_payment_pg_sync_permission", return_value=True)
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

    @patch(
        "hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayService.add_missing_records_to_payment_instructions"
    )
    @patch("hct_mis_api.apps.payment.admin.has_payment_plan_pg_sync_permission", return_value=True)
    def test_payment_post_sync_missing_records_with_payment_gateway(self: Any, mock_perm: Any, mock_sync: Any) -> None:
        url = reverse(
            "admin:payment_paymentplan_sync_missing_records_with_payment_gateway", args=[self.payment_plan.pk]
        )
        response = self.client.post(url)

        mock_sync.assert_called_once_with(self.payment_plan)
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("admin:payment_paymentplan_change", args=[self.payment_plan.pk]),
            response["Location"],
        )

    @patch("hct_mis_api.apps.payment.admin.has_payment_plan_pg_sync_permission", return_value=True)
    def test_payment_get_sync_missing_records_with_payment_gateway(self: Any, mock_perm: Any) -> None:
        url = reverse(
            "admin:payment_paymentplan_sync_missing_records_with_payment_gateway", args=[self.payment_plan.pk]
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you confirm to Sync with Payment Gateway missing Records?")

    @patch("hct_mis_api.apps.payment.admin.has_payment_plan_export_per_fsp_permission", return_value=True)
    def test_get_regenerate_export_xlsx_form(self, mock_perm: Any) -> None:
        url = reverse("admin:payment_paymentplan_regenerate_export_xlsx", args=[self.payment_plan.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a template if you want the export to include the FSP Auth Code")
        self.assertIn("form", response.context)

    @patch("hct_mis_api.apps.payment.services.payment_plan_services.PaymentPlanService.export_xlsx_per_fsp")
    @patch("hct_mis_api.apps.payment.admin.has_payment_plan_export_per_fsp_permission", return_value=True)
    def test_post_regenerate_export_xlsx_without_template(self, mock_perm: Any, mock_export: Any) -> None:
        url = reverse("admin:payment_paymentplan_regenerate_export_xlsx", args=[self.payment_plan.pk])
        response = self.client.post(url, {"template": ""})  # no template selected

        mock_export.assert_called_once_with(self.admin_user.pk, None)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:payment_paymentplan_change", args=[self.payment_plan.pk]), response["Location"])

    @patch("hct_mis_api.apps.payment.services.payment_plan_services.PaymentPlanService.export_xlsx_per_fsp")
    @patch("hct_mis_api.apps.payment.admin.has_payment_plan_export_per_fsp_permission", return_value=True)
    def test_post_regenerate_export_xlsx_with_template(self, mock_perm: Any, mock_export: Any) -> None:
        self.client.force_login(self.admin_user)
        template = FinancialServiceProviderXlsxTemplateFactory(name="Test Template AAA")
        fsp = FinancialServiceProviderFactory()
        fsp.allowed_business_areas.add(self.payment_plan.business_area)
        fsp.xlsx_templates.add(template)
        url = reverse("admin:payment_paymentplan_regenerate_export_xlsx", args=[self.payment_plan.pk])
        response = self.client.post(url, {"template": template.id})

        mock_export.assert_called_once_with(self.admin_user.pk, str(template.id))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:payment_paymentplan_change", args=[self.payment_plan.pk]), response["Location"])

    def test_can_sync_with_payment_gateway(self) -> None:
        self.assertFalse(can_sync_with_payment_gateway(self.payment_plan))

    def test_can_regenerate_export_file_per_fsp(self) -> None:
        self.assertFalse(can_regenerate_export_file_per_fsp(self.payment_plan))
