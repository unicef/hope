import pytest
from rest_framework import serializers

from hope.api.utils import CurrencySlugRelatedField
from hope.models.currency import Currency


class _CurrencyCarrierSerializer(serializers.Serializer):
    currency = CurrencySlugRelatedField(queryset=Currency.objects.all(), allow_null=True)


@pytest.mark.django_db
def test_field_resolves_active_currency():
    currency = Currency.objects.create(code="TST", name="Test", active=True)

    serializer = _CurrencyCarrierSerializer(data={"currency": "TST"})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["currency"] == currency


@pytest.mark.django_db
def test_field_resolves_active_row_for_shared_code():
    Currency.objects.create(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)
    new = Currency.objects.create(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)

    serializer = _CurrencyCarrierSerializer(data={"currency": "SYP"})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["currency"] == new


@pytest.mark.django_db
def test_field_shared_code_does_not_raise_multiple_objects_returned():
    # Two rows with the same code (one active, one deprecated): a plain SlugRelatedField
    # would raise MultipleObjectsReturned -> HTTP 500. This field must resolve cleanly.
    Currency.objects.create(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)
    Currency.objects.create(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)

    serializer = _CurrencyCarrierSerializer(data={"currency": "SYP"})

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_field_unknown_code_is_validation_error():
    serializer = _CurrencyCarrierSerializer(data={"currency": "MISSING"})

    assert not serializer.is_valid()
    assert "currency" in serializer.errors


def test_field_defaults_slug_field_to_code():
    field = CurrencySlugRelatedField(queryset=Currency.objects.all())

    assert field.slug_field == "code"


def test_field_rejects_an_overridden_slug_field():
    # Honouring another slug field would make reads use it while writes still resolved
    # by code, so the kwarg is refused outright rather than silently ignored.
    with pytest.raises(TypeError):
        CurrencySlugRelatedField(slug_field="vision_code", queryset=Currency.objects.all())


@pytest.mark.django_db
def test_field_inactive_only_code_is_validation_error():
    Currency.objects.create(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)

    serializer = _CurrencyCarrierSerializer(data={"currency": "SYP"})

    assert not serializer.is_valid()
    assert "currency" in serializer.errors
