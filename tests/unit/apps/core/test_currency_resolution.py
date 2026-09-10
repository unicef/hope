import pytest

from extras.test_utils.factories import CurrencyFactory
from hope.apps.core.currency_resolution import (
    resolve_active_currency,
    resolve_currency_for_update,
    resolve_currency_for_update_or_none,
)
from hope.models.currency import Currency

pytestmark = pytest.mark.django_db


@pytest.fixture
def syp_pair() -> tuple[Currency, Currency]:
    """The post-redenomination layout: a deprecated and an active row sharing ``code``."""
    deprecated = CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)
    active = CurrencyFactory(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)
    return deprecated, active


@pytest.fixture
def currency_eur() -> Currency:
    return CurrencyFactory(code="EUR", name="Euro", vision_code="EUR", active=True)


def test_resolve_active_currency_returns_the_active_row(syp_pair: tuple[Currency, Currency]) -> None:
    _deprecated, active = syp_pair

    assert resolve_active_currency("SYP") == active


def test_resolve_active_currency_raises_when_only_a_deprecated_row_exists() -> None:
    CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)

    with pytest.raises(Currency.DoesNotExist):
        resolve_active_currency("SYP")


def test_resolve_currency_for_update_keeps_current_row_when_code_is_unchanged(
    syp_pair: tuple[Currency, Currency],
) -> None:
    deprecated, _active = syp_pair

    assert resolve_currency_for_update("SYP", deprecated) == deprecated


def test_resolve_currency_for_update_returns_active_row_when_code_actually_changes(
    syp_pair: tuple[Currency, Currency], currency_eur: Currency
) -> None:
    _deprecated, active = syp_pair

    assert resolve_currency_for_update("SYP", currency_eur) == active


def test_resolve_currency_for_update_returns_active_row_when_there_is_no_current(
    syp_pair: tuple[Currency, Currency],
) -> None:
    _deprecated, active = syp_pair

    assert resolve_currency_for_update("SYP", None) == active


def test_resolve_currency_for_update_raises_for_a_changed_code_without_an_active_row(
    currency_eur: Currency,
) -> None:
    CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)

    with pytest.raises(Currency.DoesNotExist):
        resolve_currency_for_update("SYP", currency_eur)


def test_resolve_currency_for_update_or_none_keeps_current_row_when_code_is_unchanged(
    syp_pair: tuple[Currency, Currency],
) -> None:
    deprecated, _active = syp_pair

    assert resolve_currency_for_update_or_none("SYP", deprecated) == deprecated


def test_resolve_currency_for_update_or_none_returns_active_row_when_code_actually_changes(
    syp_pair: tuple[Currency, Currency], currency_eur: Currency
) -> None:
    _deprecated, active = syp_pair

    assert resolve_currency_for_update_or_none("SYP", currency_eur) == active


def test_resolve_currency_for_update_or_none_returns_none_for_an_unknown_code(currency_eur: Currency) -> None:
    assert resolve_currency_for_update_or_none("MISSING", currency_eur) is None


def test_resolve_currency_for_update_or_none_returns_none_when_only_a_deprecated_row_exists(
    currency_eur: Currency,
) -> None:
    CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)

    assert resolve_currency_for_update_or_none("SYP", currency_eur) is None
