from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pytest

from extras.test_utils.factories import CurrencyFactory
from hope.models.currency import Currency


@pytest.mark.django_db
def test_full_clean_backfills_vision_code_from_code():
    currency = Currency(code="TST", name="Test")

    currency.full_clean()

    assert currency.vision_code == "TST"


@pytest.mark.django_db
def test_full_clean_reports_duplicate_vision_code_as_validation_error():
    Currency.objects.create(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)
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


@pytest.mark.django_db
def test_duplicate_vision_code_raises():
    Currency.objects.create(code="XYA", name="A", vision_code="SHRD")

    with pytest.raises(IntegrityError):
        Currency.objects.create(code="XYB", name="B", vision_code="SHRD")


@pytest.mark.django_db
def test_duplicate_vision_code_case_insensitive_raises():
    Currency.objects.create(code="XYA", name="A", vision_code="shrd")

    with pytest.raises(IntegrityError):
        Currency.objects.create(code="XYB", name="B", vision_code="SHRD")


@pytest.mark.django_db
def test_two_active_rows_same_code_raises():
    Currency.objects.create(code="XYC", name="A", vision_code="XYC", active=True)

    with pytest.raises(IntegrityError):
        Currency.objects.create(code="XYC", name="B", vision_code="XYCO", active=True)


@pytest.mark.django_db
def test_two_active_rows_same_code_case_insensitive_raises():
    Currency.objects.create(code="xyc", name="A", vision_code="xyc", active=True)

    with pytest.raises(IntegrityError):
        Currency.objects.create(code="XYC", name="B", vision_code="XYCO", active=True)


@pytest.mark.django_db
def test_old_inactive_and_new_active_share_code_allowed():
    old = Currency.objects.create(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)
    new = Currency.objects.create(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)

    assert Currency.objects.filter(code="SYP").count() == 2
    assert old.active is False
    assert new.active is True


@pytest.fixture
def currency_tst(db) -> Currency:
    return CurrencyFactory(code="TST", name="Test", vision_code="TST", active=True)


@pytest.fixture
def syp_pair(db) -> tuple[Currency, Currency]:
    """The post-redenomination layout: a deprecated and an active row sharing ``code``."""
    deprecated = CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)
    active = CurrencyFactory(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)
    return deprecated, active


@pytest.fixture
def deprecated_syp(db) -> Currency:
    return CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)


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


def test_active_code_lookup_is_not_reachable_from_a_queryset(db) -> None:
    assert not hasattr(Currency.objects.filter(active=False), "get_active_by_code")
