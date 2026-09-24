import hashlib
from unittest import mock

from django.conf import settings
import pytest

from extras.test_utils.factories import (
    CurrencyFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hope.apps.activity_log.utils import create_diff
from hope.apps.payment.services.payment_household_snapshot_service import create_payment_plan_snapshot_data
from hope.models import Household, Payment, PaymentPlan
from hope.models.currency import Currency

pytestmark = pytest.mark.django_db


def test_currency_str_returns_code_and_name(currency_usd: Currency, django_assert_num_queries) -> None:
    with django_assert_num_queries(0):
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


def test_get_unore_exchange_rate_returns_1_for_usdc(payment_plan_usdc: PaymentPlan, django_assert_num_queries) -> None:
    with django_assert_num_queries(0):
        assert payment_plan_usdc.get_unore_exchange_rate() == 1.0


def test_get_unore_exchange_rate_calls_client_with_currency_code(
    payment_plan_pln: PaymentPlan, django_assert_num_queries
) -> None:
    with django_assert_num_queries(0):
        mock_client = mock.Mock()
        mock_client.get_exchange_rate_for_currency_code.return_value = 3.75

        result = payment_plan_pln.get_unore_exchange_rate(exchange_rates_client=mock_client)

        assert result == 3.75
        mock_client.get_exchange_rate_for_currency_code.assert_called_once_with(
            "PLN", payment_plan_pln.currency_exchange_date
        )


@pytest.fixture
def current_syp() -> Currency:
    return CurrencyFactory(code="SYP", name="Syrian Pound", vision_code="SYP01")


@pytest.fixture
def payment_plan_syp(current_syp: Currency) -> PaymentPlan:
    return PaymentPlanFactory(currency=current_syp)


def test_get_unore_exchange_rate_uses_vision_code_when_different_from_code(payment_plan_syp: PaymentPlan) -> None:
    payment_plan = payment_plan_syp
    mock_client = mock.Mock()
    mock_client.get_exchange_rate_for_currency_code.return_value = 0.01

    result = payment_plan.get_unore_exchange_rate(exchange_rates_client=mock_client)

    assert result == 0.01
    mock_client.get_exchange_rate_for_currency_code.assert_called_once_with(
        "SYP01", payment_plan.currency_exchange_date
    )


def test_get_unore_exchange_rate_raises_for_null_currency(
    payment_plan_no_currency: PaymentPlan, django_assert_num_queries
) -> None:
    with django_assert_num_queries(0):
        with pytest.raises(ValueError, match="Cannot get exchange rate for PaymentPlan without currency"):
            payment_plan_no_currency.get_unore_exchange_rate()


def _calculate_expected_hash(payment: Payment) -> str:
    sha1 = hashlib.blake2b(digest_size=20)
    sha1.update(settings.SECRET_KEY.encode("utf-8"))

    for field_name in payment.signature_fields:
        if "." in field_name:
            from hope.apps.core.utils import nested_getattr

            value = nested_getattr(payment, field_name, None)
        else:
            value = getattr(payment, field_name, None)
        if hasattr(payment, "_normalize"):
            value = payment._normalize(field_name, value)
        sha1.update(str(value).encode("utf-8"))
    return sha1.hexdigest()


def test_payment_signature_uses_currency_vision_code_via_dotted_path(
    payment_with_snapshot: Payment, django_assert_num_queries
) -> None:
    with django_assert_num_queries(3):
        payment_with_snapshot.save()

        assert payment_with_snapshot.signature_hash == _calculate_expected_hash(payment_with_snapshot)


@pytest.fixture
def deprecated_syp() -> Currency:
    return CurrencyFactory(code="SYP", name="Syrian Pound Old", vision_code="SYP", active=False)


@pytest.fixture
def payment_on_deprecated_syp(deprecated_syp: Currency) -> Payment:
    payment_plan = PaymentPlanFactory(currency=deprecated_syp)
    payment = PaymentFactory(parent=payment_plan, currency=deprecated_syp)
    create_payment_plan_snapshot_data(payment_plan)
    payment.refresh_from_db()
    payment.save()
    return payment


def test_payment_signature_changes_when_currency_moves_to_another_variant_of_the_same_code(
    payment_on_deprecated_syp: Payment, current_syp: Currency
) -> None:
    signature_on_deprecated_variant = payment_on_deprecated_syp.signature_hash

    payment_on_deprecated_syp.currency = current_syp
    payment_on_deprecated_syp.save()

    assert payment_on_deprecated_syp.signature_hash != signature_on_deprecated_variant


@pytest.fixture
def payment_on_syp01_before_redenomination() -> Payment:
    currency = CurrencyFactory(code="SYP01", name="Syrian Pound", vision_code="SYP01")
    payment_plan = PaymentPlanFactory(currency=currency)
    payment = PaymentFactory(parent=payment_plan, currency=currency)
    create_payment_plan_snapshot_data(payment_plan)
    payment.refresh_from_db()
    payment.save()
    return payment


def test_payment_signature_survives_redenomination_renaming_the_code(
    payment_on_syp01_before_redenomination: Payment,
) -> None:
    # The redenomination migration renames the new row's code SYP01 -> SYP and keeps its vision_code.
    signature_before = payment_on_syp01_before_redenomination.signature_hash

    payment_on_syp01_before_redenomination.currency.code = "SYP"
    payment_on_syp01_before_redenomination.save()

    assert payment_on_syp01_before_redenomination.signature_hash == signature_before


def test_payment_plan_activity_log_diff_reports_currency_code(
    payment_plan_usd: PaymentPlan,
    payment_plan_pln: PaymentPlan,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(2):
        diff = create_diff(payment_plan_usd, payment_plan_pln, PaymentPlan.ACTIVITY_LOG_MAPPING)

    assert "currency" in diff
    assert diff["currency"]["from"] == "USD"
    assert diff["currency"]["to"] == "PLN"
    assert diff["currency_vision_code"] == {"from": "USD", "to": "PLN"}


@pytest.fixture
def payment_plan_deprecated_syp(deprecated_syp: Currency) -> PaymentPlan:
    return PaymentPlanFactory(currency=deprecated_syp)


def test_payment_plan_activity_log_diff_reports_variant_change_within_the_same_code(
    payment_plan_deprecated_syp: PaymentPlan, payment_plan_syp: PaymentPlan
) -> None:
    diff = create_diff(payment_plan_deprecated_syp, payment_plan_syp, PaymentPlan.ACTIVITY_LOG_MAPPING)

    assert "currency" not in diff
    assert diff["currency_vision_code"] == {"from": "SYP", "to": "SYP01"}


def test_household_activity_log_diff_reports_currency_code(
    currency_usd: Currency,
    currency_pln: Currency,
    django_assert_num_queries,
) -> None:
    household_usd = HouseholdFactory(currency=currency_usd)
    household_pln = HouseholdFactory(
        currency=currency_pln,
        business_area=household_usd.business_area,
        program=household_usd.program,
    )

    with django_assert_num_queries(0):
        diff = create_diff(household_usd, household_pln, Household.ACTIVITY_LOG_MAPPING)

    assert "currency" in diff
    assert diff["currency"]["from"] == "USD"
    assert diff["currency"]["to"] == "PLN"
    assert diff["currency_vision_code"] == {"from": "USD", "to": "PLN"}


@pytest.fixture
def household_deprecated_syp(deprecated_syp: Currency) -> Household:
    return HouseholdFactory(currency=deprecated_syp)


@pytest.fixture
def household_current_syp(household_deprecated_syp: Household, current_syp: Currency) -> Household:
    return HouseholdFactory(
        currency=current_syp,
        business_area=household_deprecated_syp.business_area,
        program=household_deprecated_syp.program,
    )


def test_household_activity_log_diff_reports_variant_change_within_the_same_code(
    household_deprecated_syp: Household, household_current_syp: Household
) -> None:
    diff = create_diff(household_deprecated_syp, household_current_syp, Household.ACTIVITY_LOG_MAPPING)

    assert "currency" not in diff
    assert diff["currency_vision_code"] == {"from": "SYP", "to": "SYP01"}
