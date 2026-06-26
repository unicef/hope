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
def test_duplicate_code_different_vision_code_allowed():
    Currency.objects.create(code="XYC", name="Test Currency", vision_code="XYC")
    Currency.objects.create(code="XYC", name="Test Currency Alt", vision_code="XYCO")

    assert Currency.objects.filter(code="XYC").count() == 2


@pytest.mark.django_db
def test_duplicate_code_same_vision_code_raises():
    Currency.objects.create(code="XYC", name="Test Currency", vision_code="XYC")

    with pytest.raises(IntegrityError):
        Currency.objects.create(code="XYC", name="Test Currency Duplicate", vision_code="XYC")


@pytest.mark.django_db
def test_str_with_different_vision_code():
    currency = Currency(code="TST", name="Test", vision_code="TS")

    assert str(currency) == "TST (TS) - Test"


@pytest.mark.django_db
def test_str_with_same_vision_code():
    currency = Currency(code="TST", name="Test", vision_code="TST")

    assert str(currency) == "TST - Test"


@pytest.mark.django_db
def test_filter_code_first_returns_none_when_missing():
    assert Currency.objects.filter(code="NONEXISTENT").first() is None


@pytest.mark.django_db
def test_filter_code_first_returns_first_when_duplicate_codes():
    a = Currency.objects.create(code="XYC", name="A", vision_code="XYC")
    Currency.objects.create(code="XYC", name="B", vision_code="XYCO")

    result = Currency.objects.filter(code="XYC").first()

    assert result is not None
    assert result.id == a.id


@pytest.mark.django_db
def test_filter_code_exists_works_with_duplicate_codes():
    Currency.objects.create(code="XYC", name="A", vision_code="XYC")
    Currency.objects.create(code="XYC", name="B", vision_code="XYCO")

    assert Currency.objects.filter(code="XYC").exists()


@pytest.mark.django_db
def test_save_defaults_vision_code_from_code_on_create():
    currency = Currency(code="ABC", name="Test")
    currency.save()

    assert currency.vision_code == "ABC"


@pytest.mark.django_db
def test_save_preserves_explicit_vision_code_on_update():
    currency = Currency(code="ABC", name="Test", vision_code="AB")
    currency.save()

    currency.name = "Updated"
    currency.save()

    assert currency.vision_code == "AB"
