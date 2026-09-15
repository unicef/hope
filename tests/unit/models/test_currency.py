import logging

from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pytest

from extras.test_utils.factories import CurrencyFactory
from hope.models.currency import Currency


@pytest.fixture
def currency_tst(db) -> Currency:
    return CurrencyFactory(code="TST", name="Test", vision_code="TST", active=True)


@pytest.fixture
def inactive_currency(db) -> Currency:
    return CurrencyFactory(code="INA", name="Inactive", vision_code="INA", active=False)


@pytest.fixture
def syp_pair(db) -> tuple[Currency, Currency]:
    """The post-redenomination layout: a deprecated and an active row sharing ``code``."""
    deprecated = CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)
    active = CurrencyFactory(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)
    return deprecated, active


@pytest.fixture
def deprecated_syp(db) -> Currency:
    return CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)


@pytest.fixture
def retired_with_vision_code(db) -> Currency:
    """An inactive row whose ``vision_code`` differs from its ``code``, so it would be an alias if active."""
    return CurrencyFactory(code="VEF", name="Venezuelan bolivar", vision_code="VEF01", active=False)


@pytest.fixture
def deactivated_code_reused_as_alias(db) -> tuple[Currency, Currency]:
    """A withdrawn currency whose ISO code is the ``vision_code`` of a different, active currency."""
    withdrawn = CurrencyFactory(code="ZWL", name="Zimbabwean dollar", vision_code="ZWL00", active=False)
    successor = CurrencyFactory(code="ZWG", name="Zimbabwe Gold", vision_code="ZWL", active=True)
    return withdrawn, successor


@pytest.fixture
def code_shadowing_an_alias(db) -> tuple[Currency, Currency]:
    """Two active rows where one's ``code`` is the other's ``vision_code``."""
    by_code = CurrencyFactory(code="ABC", name="By code", vision_code="ABC01", active=True)
    by_alias = CurrencyFactory(code="XYZ", name="By alias", vision_code="ABC", active=True)
    return by_code, by_alias


@pytest.mark.django_db
def test_full_clean_backfills_vision_code_from_code():
    currency = Currency(code="TST", name="Test")

    currency.full_clean()

    assert currency.vision_code == "TST"


def test_full_clean_reports_duplicate_vision_code_as_validation_error(deprecated_syp: Currency):
    duplicate = Currency(code="SYP", name="Syrian pound", active=True)

    with pytest.raises(ValidationError):
        duplicate.full_clean()


@pytest.mark.django_db
def test_save_defaults_vision_code_to_code_when_blank():
    currency = Currency(code="TST", name="Test")

    currency.save()

    assert currency.vision_code == "TST"


@pytest.mark.django_db
def test_save_preserves_explicit_vision_code():
    currency = Currency(code="TST", name="Test", vision_code="TS")

    currency.save()

    assert currency.vision_code == "TS"


@pytest.mark.django_db
def test_save_refills_vision_code_when_cleared():
    currency = Currency(code="TST", name="Test", vision_code="TS")
    currency.save()

    currency.vision_code = ""
    currency.save()

    assert currency.vision_code == "TST"


@pytest.mark.django_db
def test_str_with_different_vision_code():
    currency = Currency(code="TST", name="Test", vision_code="TS")

    assert str(currency) == "TST (TS) - Test"


@pytest.mark.django_db
def test_str_with_same_vision_code():
    currency = Currency(code="TST", name="Test", vision_code="TST")

    assert str(currency) == "TST - Test"


@pytest.mark.parametrize("vision_code", ["TST", "tst"])
def test_duplicate_vision_code_raises(currency_tst: Currency, vision_code: str):
    with pytest.raises(IntegrityError):
        Currency.objects.create(code="XYB", name="B", vision_code=vision_code)


@pytest.mark.parametrize("code", ["TST", "tst"])
def test_two_active_rows_same_code_raises(currency_tst: Currency, code: str):
    with pytest.raises(IntegrityError):
        Currency.objects.create(code=code, name="B", vision_code="TSTO", active=True)


def test_old_inactive_and_new_active_share_code_allowed(deprecated_syp: Currency):
    new = Currency.objects.create(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)

    assert set(Currency.objects.filter(code="SYP").values_list("pk", "active")) == {
        (deprecated_syp.pk, False),
        (new.pk, True),
    }


def test_get_active_by_code_returns_active_row(currency_tst: Currency) -> None:
    assert Currency.objects.get_active_by_code("TST") == currency_tst


def test_get_active_by_code_raises_when_no_active_match(db) -> None:
    with pytest.raises(Currency.DoesNotExist):
        Currency.objects.get_active_by_code("MISSING")


def test_get_active_by_code_prefers_active_over_deprecated_for_shared_code(
    syp_pair: tuple[Currency, Currency],
) -> None:
    # Business scenario: old (SYP, SYP) deprecated + new (SYP, SYP01) active.
    # Ambiguous "SYP" input must resolve to the NEW (active) row, never the deprecated one.
    _deprecated, active = syp_pair

    assert Currency.objects.get_active_by_code("SYP") == active


def test_get_active_by_code_raises_when_only_deprecated_row_exists(deprecated_syp: Currency) -> None:
    with pytest.raises(Currency.DoesNotExist):
        Currency.objects.get_active_by_code("SYP")


def test_get_active_by_code_or_none_returns_active_row(currency_tst: Currency) -> None:
    assert Currency.objects.get_active_by_code_or_none("TST") == currency_tst


def test_get_active_by_code_or_none_returns_none_for_unknown_code(db) -> None:
    assert Currency.objects.get_active_by_code_or_none("MISSING") is None


def test_get_active_by_code_or_none_returns_none_when_only_deprecated_row_exists(
    deprecated_syp: Currency,
) -> None:
    assert Currency.objects.get_active_by_code_or_none("SYP") is None


def test_get_active_by_code_or_none_prefers_active_over_deprecated_for_shared_code(
    syp_pair: tuple[Currency, Currency],
) -> None:
    _deprecated, active = syp_pair

    assert Currency.objects.get_active_by_code_or_none("SYP") == active


def test_get_active_by_code_resolves_the_vision_code_alias_of_the_active_row(
    syp_pair: tuple[Currency, Currency],
) -> None:
    _deprecated, active = syp_pair

    assert Currency.objects.get_active_by_code("SYP01") == active


def test_get_active_by_code_or_none_resolves_the_vision_code_alias_of_the_active_row(
    syp_pair: tuple[Currency, Currency],
) -> None:
    _deprecated, active = syp_pair

    assert Currency.objects.get_active_by_code_or_none("SYP01") == active


def test_get_active_by_code_resolves_a_code_in_one_query(
    syp_pair: tuple[Currency, Currency], django_assert_num_queries
) -> None:
    # The alias lookups are paid only when no active row matches by code.
    with django_assert_num_queries(1):
        Currency.objects.get_active_by_code("SYP")


def test_get_active_by_code_logs_a_resolution_through_the_alias(
    syp_pair: tuple[Currency, Currency], caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.WARNING, logger="hope.models.currency"):
        Currency.objects.get_active_by_code("SYP01")

    assert [record.getMessage() for record in caplog.records] == [
        "Currency 'SYP01' resolved through the vision_code alias of 'SYP'."
    ]


def test_get_active_by_code_does_not_log_a_resolution_by_code(
    syp_pair: tuple[Currency, Currency], caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.WARNING, logger="hope.models.currency"):
        Currency.objects.get_active_by_code("SYP")

    assert caplog.records == []


def test_get_active_by_code_prefers_a_code_over_another_rows_vision_code(
    code_shadowing_an_alias: tuple[Currency, Currency],
) -> None:
    by_code, _by_alias = code_shadowing_an_alias

    assert Currency.objects.get_active_by_code("ABC") == by_code


def test_get_active_by_code_raises_for_the_vision_code_of_an_inactive_row(
    retired_with_vision_code: Currency,
) -> None:
    with pytest.raises(Currency.DoesNotExist):
        Currency.objects.get_active_by_code("VEF01")


def test_get_active_by_code_or_none_returns_none_for_the_vision_code_of_an_inactive_row(
    retired_with_vision_code: Currency,
) -> None:
    assert Currency.objects.get_active_by_code_or_none("VEF01") is None


def test_get_active_by_code_raises_for_a_deactivated_code_reused_as_an_alias(
    deactivated_code_reused_as_alias: tuple[Currency, Currency],
) -> None:
    with pytest.raises(Currency.DoesNotExist):
        Currency.objects.get_active_by_code("ZWL")


def test_get_active_by_code_or_none_returns_none_for_a_deactivated_code_reused_as_an_alias(
    deactivated_code_reused_as_alias: tuple[Currency, Currency],
) -> None:
    assert Currency.objects.get_active_by_code_or_none("ZWL") is None


def test_active_code_lookup_is_not_reachable_from_a_queryset(db) -> None:
    assert not hasattr(Currency.objects.filter(active=False), "get_active_by_code")


def test_active_excludes_inactive_currencies(
    currency_tst: Currency, inactive_currency: Currency, django_assert_num_queries
) -> None:
    with django_assert_num_queries(1):
        result = list(Currency.objects.active())

    assert result == [currency_tst]


def test_active_returns_only_active_row_for_shared_code(
    syp_pair: tuple[Currency, Currency], django_assert_num_queries
) -> None:
    _deprecated, active = syp_pair

    with django_assert_num_queries(1):
        result = list(Currency.objects.active())

    assert result == [active]


def test_active_is_chainable(inactive_currency: Currency) -> None:
    assert Currency.objects.active().filter(code="INA").exists() is False
