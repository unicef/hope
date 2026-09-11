"""Tests for services that use Currency FK."""

from decimal import Decimal
from unittest.mock import Mock

from django.utils import timezone
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    CurrencyFactory,
    DeliveryMechanismFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hope.apps.household.api.serializers.household import DeliveredQuantitySerializer
from hope.apps.household.services.household_programs_with_delivered_quantity import (
    delivered_quantity_service,
)
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.apps.payment.utils import get_quantity_in_usd
from hope.models import DeliveryMechanism, Household
from hope.models.currency import Currency

pytestmark = pytest.mark.django_db


def test_get_quantity_in_usd_with_string_currency(currency_pln: Currency, django_assert_num_queries) -> None:
    exchange_rates_client = Mock()
    exchange_rates_client.get_exchange_rate_for_currency_code.return_value = 4

    with django_assert_num_queries(0):
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


def test_get_quantity_in_usd_with_currency_instance(currency_pln: Currency, django_assert_num_queries) -> None:
    exchange_rates_client = Mock()
    exchange_rates_client.get_exchange_rate_for_currency_code.return_value = 4

    with django_assert_num_queries(0):
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


def test_get_quantity_in_usd_with_currency_instance_and_provided_rate(
    currency_pln: Currency, django_assert_num_queries
) -> None:
    with django_assert_num_queries(0):
        result = get_quantity_in_usd(
            amount=Decimal(10),
            currency=currency_pln,
            exchange_rate=2,
            currency_exchange_date=timezone.now(),
        )

        assert result == Decimal("5.00")


def test_delivered_quantity_service_returns_currency_codes(
    currency_usd: Currency, currency_pln: Currency, django_assert_num_queries
) -> None:
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

    with django_assert_num_queries(2):
        results = delivered_quantity_service(household)

    # First entry is always the USD aggregate
    assert results[0]["currency"] == "USD"
    # Non-USD entries should have string currency codes, not integer PKs
    non_usd = [r for r in results if r["currency"] != "USD"]
    assert len(non_usd) == 1
    assert non_usd[0]["currency"] == "PLN"
    assert non_usd[0]["total_delivered_quantity"] == Decimal("200.00")


def test_delivered_quantity_service_excludes_usd_from_per_currency(
    currency_usd: Currency, django_assert_num_queries
) -> None:
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

    with django_assert_num_queries(2):
        results = delivered_quantity_service(household)

    assert len(results) == 1
    assert results[0]["currency"] == "USD"


def test_validate_transfer_to_digital_wallet_rejects_usdc_with_non_digital(
    currency_usdc: Currency, django_assert_num_queries
) -> None:
    dm = DeliveryMechanismFactory(transfer_type=DeliveryMechanism.TransferType.CASH)
    pp = PaymentPlanFactory(currency=currency_usdc, delivery_mechanism=dm)
    service = PaymentPlanService(pp)

    with django_assert_num_queries(0), pytest.raises(ValidationError, match="Transfer to Digital Wallet"):
        service._validate_transfer_to_digital_wallet_and_usdc(currency_usdc)


def test_validate_transfer_to_digital_wallet_rejects_non_usdc_with_digital(
    currency_pln: Currency, django_assert_num_queries
) -> None:
    dm = DeliveryMechanismFactory(transfer_type=DeliveryMechanism.TransferType.DIGITAL)
    pp = PaymentPlanFactory(currency=currency_pln, delivery_mechanism=dm)
    service = PaymentPlanService(pp)

    with django_assert_num_queries(0), pytest.raises(ValidationError, match="Transfer to Digital Wallet"):
        service._validate_transfer_to_digital_wallet_and_usdc(currency_pln)


def test_validate_transfer_to_digital_wallet_accepts_usdc_with_digital(
    currency_usdc: Currency, django_assert_num_queries
) -> None:
    dm = DeliveryMechanismFactory(transfer_type=DeliveryMechanism.TransferType.DIGITAL)
    pp = PaymentPlanFactory(currency=currency_usdc, delivery_mechanism=dm)
    service = PaymentPlanService(pp)
    with django_assert_num_queries(0):
        service._validate_transfer_to_digital_wallet_and_usdc(currency_usdc)


@pytest.fixture
def syp_denominations(db) -> tuple[Currency, Currency]:
    """The two rows a redenomination leaves behind, sharing one ISO `code`."""
    deprecated = CurrencyFactory(code="SYP", vision_code="SYP", name="Syrian Pound", active=False)
    active = CurrencyFactory(code="SYP", vision_code="SYP01", name="Syrian Pound", active=True)
    return deprecated, active


@pytest.fixture
def household_paid_in_both_syp_denominations(
    currency_usd: Currency, syp_denominations: tuple[Currency, Currency]
) -> Household:
    deprecated_syp, active_syp = syp_denominations
    pp = PaymentPlanFactory()
    household = HouseholdFactory(
        currency=currency_usd,
        business_area=pp.business_area,
        program=pp.program_cycle.program,
    )
    PaymentFactory(
        parent=pp,
        household=household,
        currency=deprecated_syp,
        delivered_quantity=Decimal("100.00"),
        delivered_quantity_usd=Decimal("1.00"),
    )
    # One Payment per (plan, household), so the second denomination needs its own plan.
    pp2 = PaymentPlanFactory(program_cycle=pp.program_cycle, business_area=pp.business_area)
    PaymentFactory(
        parent=pp2,
        household=household,
        currency=active_syp,
        delivered_quantity=Decimal("1.00"),
        delivered_quantity_usd=Decimal("1.00"),
    )
    return household


@pytest.fixture
def household_paid_in_pln(currency_usd: Currency, currency_pln: Currency) -> Household:
    pp = PaymentPlanFactory()
    household = HouseholdFactory(
        currency=currency_usd,
        business_area=pp.business_area,
        program=pp.program_cycle.program,
    )
    PaymentFactory(
        parent=pp,
        household=household,
        currency=currency_pln,
        delivered_quantity=Decimal("200.00"),
        delivered_quantity_usd=Decimal("50.00"),
    )
    return household


def test_delivered_quantity_service_keeps_two_denominations_of_one_code_apart(
    household_paid_in_both_syp_denominations: Household,
) -> None:
    results = delivered_quantity_service(household_paid_in_both_syp_denominations)

    assert results == [
        {"currency": "USD", "currency_vision_code": "USD", "total_delivered_quantity": Decimal("2.00")},
        {"currency": "SYP", "currency_vision_code": "SYP", "total_delivered_quantity": Decimal("100.00")},
        {"currency": "SYP", "currency_vision_code": "SYP01", "total_delivered_quantity": Decimal("1.00")},
    ]


def test_delivered_quantity_serializer_publishes_the_denomination_of_each_entry(
    household_paid_in_both_syp_denominations: Household,
) -> None:
    quantities = delivered_quantity_service(household_paid_in_both_syp_denominations)

    data = DeliveredQuantitySerializer(quantities, many=True).data

    assert data == [
        {"currency": "USD", "currency_vision_code": "USD", "total_delivered_quantity": "2.00"},
        {"currency": "SYP", "currency_vision_code": "SYP", "total_delivered_quantity": "100.00"},
        {"currency": "SYP", "currency_vision_code": "SYP01", "total_delivered_quantity": "1.00"},
    ]


def test_delivered_quantity_service_reports_vision_code_for_a_single_denomination(
    household_paid_in_pln: Household,
) -> None:
    results = delivered_quantity_service(household_paid_in_pln)

    assert results[0] == {
        "currency": "USD",
        "currency_vision_code": "USD",
        "total_delivered_quantity": Decimal("50.00"),
    }
    assert results[1] == {
        "currency": "PLN",
        "currency_vision_code": "PLN",
        "total_delivered_quantity": Decimal("200.00"),
    }
