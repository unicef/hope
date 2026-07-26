from django.db import IntegrityError
import pytest

from hope.models.currency import Currency


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


@pytest.mark.django_db
def test_resolve_code_returns_active_row():
    currency = Currency.objects.create(code="TST", name="Test", active=True)

    assert Currency.objects.resolve_code("TST") == currency


@pytest.mark.django_db
def test_resolve_code_raises_when_no_active_match():
    with pytest.raises(Currency.DoesNotExist):
        Currency.objects.resolve_code("MISSING")


@pytest.mark.django_db
def test_resolve_code_prefers_active_over_deprecated_for_shared_code():
    # Business scenario: old (SYP, SYP) deprecated + new (SYP, SYP01) active.
    # Ambiguous "SYP" input must resolve to the NEW (active) row, never the deprecated one.
    Currency.objects.create(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)
    new = Currency.objects.create(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)

    assert Currency.objects.resolve_code("SYP") == new


@pytest.mark.django_db
def test_resolve_code_raises_when_only_deprecated_row_exists():
    Currency.objects.create(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)

    with pytest.raises(Currency.DoesNotExist):
        Currency.objects.resolve_code("SYP")
