from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hope.apps.payment.services.mark_as_failed import mark_as_failed, revert_mark_as_failed
from hope.models import FinancialServiceProvider, Payment

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


def test_mark_as_failed_and_revert_update_household_cash_received() -> None:
    fsp_xlsx = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
    )
    payment_plan = PaymentPlanFactory(financial_service_provider=fsp_xlsx)
    payment_plan.payment_plan_group.exchange_rate = Decimal("2.00")
    payment_plan.payment_plan_group.save(update_fields=["exchange_rate"])
    payment = PaymentFactory(
        parent=payment_plan,
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
        entitlement_quantity=Decimal("100.00"),
        delivered_quantity=Decimal("100.00"),
        delivered_quantity_usd=Decimal("50.00"),
    )
    household = payment.household
    household.total_cash_received = Decimal("100.00")
    household.total_cash_received_usd = Decimal("50.00")
    household.save()

    mark_as_failed(payment)

    household.refresh_from_db()
    assert household.total_cash_received == 0
    assert household.total_cash_received_usd == 0

    revert_mark_as_failed(payment, Decimal("60.00"), payment_plan.dispersion_start_date)

    household.refresh_from_db()
    assert household.total_cash_received == Decimal("60.00")
    assert household.total_cash_received_usd == Decimal("30.00")
