from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hope.apps.payment.services.mark_as_failed import mark_as_failed, revert_mark_as_failed
from hope.models import FinancialServiceProvider

pytestmark = pytest.mark.django_db


def test_mark_as_failed_raises_for_payment_gateway_plan() -> None:
    fsp_api = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
    )
    payment_plan = PaymentPlanFactory(financial_service_provider=fsp_api)
    payment = PaymentFactory(parent=payment_plan, entitlement_quantity=Decimal("1.00"))

    with pytest.raises(
        DRFValidationError,
        match="Payments in payment gateway plans cannot be manually marked as failed",
    ):
        mark_as_failed(payment)


def test_mark_as_failed_raises_for_payment_plan_with_payment_gateway_flag() -> None:
    fsp_xlsx = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
    )
    payment_plan = PaymentPlanFactory(financial_service_provider=fsp_xlsx, use_payment_gateway=True)
    payment = PaymentFactory(parent=payment_plan, entitlement_quantity=Decimal("1.00"))

    with pytest.raises(
        DRFValidationError,
        match="Payments in payment gateway plans cannot be manually marked as failed",
    ):
        mark_as_failed(payment)


def test_revert_mark_as_failed_raises_for_payment_gateway_plan() -> None:
    fsp_api = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
    )
    payment_plan = PaymentPlanFactory(financial_service_provider=fsp_api)
    payment = PaymentFactory(parent=payment_plan, entitlement_quantity=Decimal("1.00"))

    with pytest.raises(
        DRFValidationError,
        match="Payments in payment gateway plans cannot be manually marked as failed",
    ):
        revert_mark_as_failed(payment, Decimal("1.00"), payment_plan.dispersion_start_date)


def test_revert_mark_as_failed_raises_for_payment_plan_with_payment_gateway_flag() -> None:
    fsp_xlsx = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
    )
    payment_plan = PaymentPlanFactory(financial_service_provider=fsp_xlsx, use_payment_gateway=True)
    payment = PaymentFactory(parent=payment_plan, entitlement_quantity=Decimal("1.00"))

    with pytest.raises(
        DRFValidationError,
        match="Payments in payment gateway plans cannot be manually marked as failed",
    ):
        revert_mark_as_failed(payment, Decimal("1.00"), payment_plan.dispersion_start_date)
