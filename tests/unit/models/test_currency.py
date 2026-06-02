import pytest

from hope.models.currency import Currency


@pytest.mark.django_db
def test_save_defaults_vision_code_to_code_when_blank():
    currency = Currency(code="EUR", name="Euro")

    currency.save()

    assert currency.vision_code == "EUR"


@pytest.mark.django_db
def test_save_preserves_explicit_vision_code():
    currency = Currency(code="EUR", name="Euro", vision_code="EU")

    currency.save()

    assert currency.vision_code == "EU"


@pytest.mark.django_db
def test_save_refills_vision_code_when_cleared():
    currency = Currency(code="EUR", name="Euro", vision_code="EU")
    currency.save()

    currency.vision_code = ""
    currency.save()

    assert currency.vision_code == "EUR"
