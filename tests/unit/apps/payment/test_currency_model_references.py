import hashlib
from unittest import mock

from django.conf import settings
import pytest

from extras.test_utils.factories import (
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hope.apps.activity_log.utils import create_diff
from hope.apps.payment.services.payment_household_snapshot_service import create_payment_plan_snapshot_data
from hope.models import Household, Payment, PaymentPlan
from hope.models.currency import Currency

pytestmark = pytest.mark.django_db


def test_currency_str_returns_code_and_name(currency_usd: Currency) -> None:
    assert str(currency_usd) == "USD - United States Dollar"


@pytest.fixture
def payment_plan_usdc(currency_usdc: Currency) -> PaymentPlan:
    return PaymentPlanFactory(currency=currency_usdc)


@pytest.fixture
def payment_plan_pln(currency_pln: Currency) -> PaymentPlan:
    return PaymentPlanFactory(currency=currency_pln)


@pytest.fixture
def payment_plan_no_currency() -> PaymentPlan:
    return PaymentPlanFactory(currency=None)


@pytest.fixture
def payment_plan_usd(currency_usd: Currency) -> PaymentPlan:
    return PaymentPlanFactory(currency=currency_usd)


@pytest.fixture
def payment_with_snapshot(payment_plan_pln: PaymentPlan, currency_pln: Currency) -> Payment:
    payment = PaymentFactory(parent=payment_plan_pln, currency=currency_pln)
    create_payment_plan_snapshot_data(payment_plan_pln)
    payment.refresh_from_db()
    return payment


def test_get_unore_exchange_rate_returns_1_for_usdc(payment_plan_usdc: PaymentPlan) -> None:
    assert payment_plan_usdc.get_unore_exchange_rate() == 1.0


def test_get_unore_exchange_rate_calls_client_with_currency_code(payment_plan_pln: PaymentPlan) -> None:
    mock_client = mock.Mock()
    mock_client.get_exchange_rate_for_currency_code.return_value = 3.75

    result = payment_plan_pln.get_unore_exchange_rate(exchange_rates_client=mock_client)

    assert result == 3.75
    mock_client.get_exchange_rate_for_currency_code.assert_called_once_with(
        "PLN", payment_plan_pln.currency_exchange_date
    )


def test_get_unore_exchange_rate_raises_for_null_currency(payment_plan_no_currency: PaymentPlan) -> None:
    with pytest.raises(ValueError, match="Cannot get exchange rate for PaymentPlan without currency"):
        payment_plan_no_currency.get_unore_exchange_rate()


def _calculate_expected_hash(payment: Payment) -> str:
    sha1 = hashlib.sha1()
    sha1.update(settings.SECRET_KEY.encode("utf-8"))

    for field_name in payment.signature_fields:
        if "." in field_name:
            from hope.apps.core.utils import nested_getattr

            value = nested_getattr(payment, field_name, None)
        else:
            value = getattr(payment, field_name, None)
        # Replicate _normalize: skip normalization for dotted names
        if "." not in field_name and hasattr(payment, "_normalize"):
            value = payment._normalize(field_name, value)
        sha1.update(str(value).encode("utf-8"))
    return sha1.hexdigest()


def test_payment_signature_uses_currency_code_via_dotted_path(payment_with_snapshot: Payment) -> None:
    payment_with_snapshot.save()

    assert payment_with_snapshot.signature_hash == _calculate_expected_hash(payment_with_snapshot)


# -- activity log diff tests --


def test_payment_plan_activity_log_diff_reports_currency_code(
    payment_plan_usd: PaymentPlan,
    payment_plan_pln: PaymentPlan,
) -> None:
    diff = create_diff(payment_plan_usd, payment_plan_pln, PaymentPlan.ACTIVITY_LOG_MAPPING)

    assert "currency" in diff
    assert diff["currency"]["from"] == "USD"
    assert diff["currency"]["to"] == "PLN"


def test_household_activity_log_diff_reports_currency_code(
    currency_usd: Currency,
    currency_pln: Currency,
) -> None:
    household_usd = HouseholdFactory(currency=currency_usd)
    household_pln = HouseholdFactory(
        currency=currency_pln,
        business_area=household_usd.business_area,
        program=household_usd.program,
    )

    diff = create_diff(household_usd, household_pln, Household.ACTIVITY_LOG_MAPPING)

    assert "currency" in diff
    assert diff["currency"]["from"] == "USD"
    assert diff["currency"]["to"] == "PLN"
