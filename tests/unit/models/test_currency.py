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
