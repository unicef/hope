"""Tests for services that use Currency FK."""

from decimal import Decimal
from unittest.mock import Mock

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    DeliveryMechanismFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from extras.test_utils.queries import assert_db_queries_num
from hope.apps.household.services.household_programs_with_delivered_quantity import (
    delivered_quantity_service,
)
from hope.apps.payment.utils import get_quantity_in_usd
from hope.models import DeliveryMechanism
from hope.models.currency import Currency

pytestmark = pytest.mark.django_db


@assert_db_queries_num(0)
def test_get_quantity_in_usd_with_string_currency(currency_pln: Currency) -> None:
    exchange_rates_client = Mock()
    exchange_rates_client.get_exchange_rate_for_currency_code.return_value = 4

    result = get_quantity_in_usd(
        amount=Decimal(20),
        currency=currency_pln,
        exchange_rate=0,
        currency_exchange_date=timezone.now(),
        exchange_rates_client=exchange_rates_client,
    )

    call_args = exchange_rates_client.get_exchange_rate_for_currency_code.call_args
    assert call_args[0][0] == "PLN"
    assert result == Decimal("5.00")


@assert_db_queries_num(0)
def test_get_quantity_in_usd_with_currency_instance(currency_pln: Currency) -> None:
    exchange_rates_client = Mock()
    exchange_rates_client.get_exchange_rate_for_currency_code.return_value = 4

    result = get_quantity_in_usd(
        amount=Decimal(20),
        currency=currency_pln,
        exchange_rate=0,
        currency_exchange_date=timezone.now(),
        exchange_rates_client=exchange_rates_client,
    )

    exchange_rates_client.get_exchange_rate_for_currency_code.assert_called_once()
    call_args = exchange_rates_client.get_exchange_rate_for_currency_code.call_args
    assert call_args[0][0] == "PLN"
    assert result == Decimal("5.00")


@assert_db_queries_num(0)
def test_get_quantity_in_usd_with_currency_instance_and_provided_rate(currency_pln: Currency) -> None:
    result = get_quantity_in_usd(
        amount=Decimal(10),
        currency=currency_pln,
        exchange_rate=2,
        currency_exchange_date=timezone.now(),
    )

    assert result == Decimal("5.00")


# -- delivered_quantity_service uses FK lookups --


@assert_db_queries_num(132)
def test_delivered_quantity_service_returns_currency_codes(currency_usd: Currency, currency_pln: Currency) -> None:
    pp = PaymentPlanFactory()
    household = HouseholdFactory(
        currency=currency_usd,
        business_area=pp.business_area,
        program=pp.program_cycle.program,
    )
    PaymentFactory(
        parent=pp,
        household=household,
        currency=currency_usd,
        delivered_quantity=Decimal("100.00"),
        delivered_quantity_usd=Decimal("100.00"),
    )
    pp2 = PaymentPlanFactory(
        program_cycle=pp.program_cycle,
        business_area=pp.business_area,
    )
    PaymentFactory(
        parent=pp2,
        household=household,
        currency=currency_pln,
        delivered_quantity=Decimal("200.00"),
        delivered_quantity_usd=Decimal("50.00"),
    )

    results = delivered_quantity_service(household)

    # First entry is always the USD aggregate
    assert results[0]["currency"] == "USD"
    # Non-USD entries should have string currency codes, not integer PKs
    non_usd = [r for r in results if r["currency"] != "USD"]
    assert len(non_usd) == 1
    assert non_usd[0]["currency"] == "PLN"
    assert non_usd[0]["total_delivered_quantity"] == Decimal("200.00")


@assert_db_queries_num(111)
def test_delivered_quantity_service_excludes_usd_from_per_currency(currency_usd: Currency) -> None:
    pp = PaymentPlanFactory()
    household = HouseholdFactory(
        currency=currency_usd,
        business_area=pp.business_area,
        program=pp.program_cycle.program,
    )
    PaymentFactory(
        parent=pp,
        household=household,
        currency=currency_usd,
        delivered_quantity=Decimal("100.00"),
        delivered_quantity_usd=Decimal("100.00"),
    )

    results = delivered_quantity_service(household)

    # Only the USD aggregate row, no per-currency duplicates
    assert len(results) == 1
    assert results[0]["currency"] == "USD"


# -- USDC validation uses .code --


@assert_db_queries_num(83)
def test_validate_transfer_to_digital_wallet_rejects_usdc_with_non_digital(currency_usdc: Currency) -> None:
    from rest_framework.exceptions import ValidationError

    from hope.apps.payment.services.payment_plan_services import PaymentPlanService

    dm = DeliveryMechanismFactory(transfer_type=DeliveryMechanism.TransferType.CASH)
    pp = PaymentPlanFactory(currency=currency_usdc, delivery_mechanism=dm)
    service = PaymentPlanService(pp)

    with pytest.raises(ValidationError, match="Transfer to Digital Wallet"):
        service._validate_transfer_to_digital_wallet_and_usdc(currency_usdc)


@assert_db_queries_num(83)
def test_validate_transfer_to_digital_wallet_rejects_non_usdc_with_digital(currency_pln: Currency) -> None:
    from rest_framework.exceptions import ValidationError

    from hope.apps.payment.services.payment_plan_services import PaymentPlanService

    dm = DeliveryMechanismFactory(transfer_type=DeliveryMechanism.TransferType.DIGITAL)
    pp = PaymentPlanFactory(currency=currency_pln, delivery_mechanism=dm)
    service = PaymentPlanService(pp)

    with pytest.raises(ValidationError, match="Transfer to Digital Wallet"):
        service._validate_transfer_to_digital_wallet_and_usdc(currency_pln)


@assert_db_queries_num(83)
def test_validate_transfer_to_digital_wallet_accepts_usdc_with_digital(currency_usdc: Currency) -> None:
    from hope.apps.payment.services.payment_plan_services import PaymentPlanService

    dm = DeliveryMechanismFactory(transfer_type=DeliveryMechanism.TransferType.DIGITAL)
    pp = PaymentPlanFactory(currency=currency_usdc, delivery_mechanism=dm)
    service = PaymentPlanService(pp)

    # Should not raise
    service._validate_transfer_to_digital_wallet_and_usdc(currency_usdc)
