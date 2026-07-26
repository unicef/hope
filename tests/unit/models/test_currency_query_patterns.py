import pytest

from hope.apps.universal_update_script.universal_individual_update_service.validator_and_handlers import (
    handle_currency_field,
    validate_currency,
)
from hope.models.currency import Currency


@pytest.mark.django_db
def test_handle_currency_field_returns_none_for_none():
    assert handle_currency_field(None, "currency", None, None, None) is None


@pytest.mark.django_db
def test_handle_currency_field_returns_none_for_empty():
    assert handle_currency_field("", "currency", None, None, None) is None


@pytest.mark.django_db
def test_handle_currency_field_returns_active_currency():
    currency = Currency.objects.create(code="TST", name="Test", active=True)

    assert handle_currency_field("TST", "currency", None, None, None) == currency


@pytest.mark.django_db
def test_handle_currency_field_resolves_active_row_for_shared_code():
    Currency.objects.create(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)
    new = Currency.objects.create(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)

    assert handle_currency_field("SYP", "currency", None, None, None) == new


@pytest.mark.django_db
def test_handle_currency_field_returns_none_for_unknown_code():
    assert handle_currency_field("MISSING", "currency", None, None, None) is None


@pytest.mark.django_db
def test_validate_currency_returns_none_for_active_code():
    Currency.objects.create(code="TST", name="Test", active=True)

    assert validate_currency("TST", "currency", None, None, None) is None


@pytest.mark.django_db
def test_validate_currency_returns_error_for_unknown_code():
    result = validate_currency("MISSING", "currency", None, None, None)

    assert result is not None
    assert "Invalid currency code" in result


@pytest.mark.django_db
def test_validate_currency_returns_error_for_inactive_only_code():
    Currency.objects.create(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)

    result = validate_currency("SYP", "currency", None, None, None)

    assert result is not None
    assert "Invalid currency code" in result


@pytest.mark.django_db
def test_validate_currency_returns_none_for_none():
    assert validate_currency(None, "currency", None, None, None) is None


@pytest.mark.django_db
def test_active_excludes_inactive_currencies():
    active = Currency.objects.create(code="ACT", name="Active", active=True)
    Currency.objects.create(code="INA", name="Inactive", active=False)

    assert list(Currency.objects.active()) == [active]


@pytest.mark.django_db
def test_active_returns_only_active_row_for_shared_code():
    Currency.objects.create(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)
    new = Currency.objects.create(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)

    assert list(Currency.objects.active()) == [new]


@pytest.mark.django_db
def test_active_is_chainable():
    Currency.objects.create(code="ACT", name="Active", active=True)
    Currency.objects.create(code="INA", name="Inactive", active=False)

    assert Currency.objects.active().filter(code="INA").exists() is False
