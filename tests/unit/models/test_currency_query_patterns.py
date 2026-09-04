import pytest

from extras.test_utils.factories import CurrencyFactory
from hope.apps.universal_update_script.universal_individual_update_service.validator_and_handlers import (
    handle_currency_field,
    validate_currency,
)
from hope.models.currency import Currency

pytestmark = pytest.mark.django_db


@pytest.fixture
def active_currency() -> Currency:
    return CurrencyFactory(code="TST", name="Test", vision_code="TST", active=True)


@pytest.fixture
def inactive_currency() -> Currency:
    return CurrencyFactory(code="INA", name="Inactive", vision_code="INA", active=False)


@pytest.fixture
def deprecated_syp() -> Currency:
    return CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)


@pytest.fixture
def current_syp() -> Currency:
    return CurrencyFactory(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)


def test_handle_currency_field_returns_none_for_none(django_assert_num_queries) -> None:
    with django_assert_num_queries(0):
        assert handle_currency_field(None, "currency", None, None, None) is None


def test_handle_currency_field_returns_none_for_empty(django_assert_num_queries) -> None:
    with django_assert_num_queries(0):
        assert handle_currency_field("", "currency", None, None, None) is None


def test_handle_currency_field_returns_active_currency(active_currency: Currency, django_assert_num_queries) -> None:
    with django_assert_num_queries(1):
        result = handle_currency_field("TST", "currency", None, None, None)

    assert result == active_currency


def test_handle_currency_field_resolves_active_row_for_shared_code(
    deprecated_syp: Currency, current_syp: Currency, django_assert_num_queries
) -> None:
    with django_assert_num_queries(1):
        result = handle_currency_field("SYP", "currency", None, None, None)

    assert result == current_syp


def test_handle_currency_field_returns_none_for_unknown_code(django_assert_num_queries) -> None:
    with django_assert_num_queries(1):
        assert handle_currency_field("MISSING", "currency", None, None, None) is None


def test_handle_currency_field_returns_none_when_only_deprecated_row_exists(
    deprecated_syp: Currency, django_assert_num_queries
) -> None:
    with django_assert_num_queries(1):
        assert handle_currency_field("SYP", "currency", None, None, None) is None


def test_validate_currency_returns_none_for_active_code(active_currency: Currency, django_assert_num_queries) -> None:
    with django_assert_num_queries(1):
        assert validate_currency("TST", "currency", None, None, None) is None


def test_validate_currency_returns_error_for_unknown_code(django_assert_num_queries) -> None:
    with django_assert_num_queries(1):
        result = validate_currency("MISSING", "currency", None, None, None)

    assert result is not None
    assert "Invalid currency code" in result


def test_validate_currency_returns_error_for_inactive_only_code(
    deprecated_syp: Currency, django_assert_num_queries
) -> None:
    with django_assert_num_queries(1):
        result = validate_currency("SYP", "currency", None, None, None)

    assert result is not None
    assert "Invalid currency code" in result


def test_validate_currency_returns_none_for_none(django_assert_num_queries) -> None:
    with django_assert_num_queries(0):
        assert validate_currency(None, "currency", None, None, None) is None


def test_active_excludes_inactive_currencies(
    active_currency: Currency, inactive_currency: Currency, django_assert_num_queries
) -> None:
    with django_assert_num_queries(1):
        result = list(Currency.objects.active())

    assert result == [active_currency]


def test_active_returns_only_active_row_for_shared_code(
    deprecated_syp: Currency, current_syp: Currency, django_assert_num_queries
) -> None:
    with django_assert_num_queries(1):
        result = list(Currency.objects.active())

    assert result == [current_syp]


def test_active_is_chainable(active_currency: Currency, inactive_currency: Currency) -> None:
    assert Currency.objects.active().filter(code="INA").exists() is False
