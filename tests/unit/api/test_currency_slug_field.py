import pytest
from rest_framework import serializers

from extras.test_utils.factories import CurrencyFactory
from hope.api.utils import CurrencySlugRelatedField
from hope.models.currency import Currency

pytestmark = pytest.mark.django_db


class _CurrencyCarrierSerializer(serializers.Serializer):
    currency = CurrencySlugRelatedField(queryset=Currency.objects.all(), allow_null=True)


@pytest.fixture
def active_currency() -> Currency:
    return CurrencyFactory(code="TST", name="Test", vision_code="TST", active=True)


@pytest.fixture
def deprecated_syp() -> Currency:
    return CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)


@pytest.fixture
def current_syp() -> Currency:
    return CurrencyFactory(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)


def test_field_resolves_active_currency(active_currency: Currency, django_assert_num_queries) -> None:
    serializer = _CurrencyCarrierSerializer(data={"currency": "TST"})

    with django_assert_num_queries(1):
        is_valid = serializer.is_valid()

    assert is_valid, serializer.errors
    assert serializer.validated_data["currency"] == active_currency


def test_field_resolves_active_row_for_shared_code(
    deprecated_syp: Currency, current_syp: Currency, django_assert_num_queries
) -> None:
    serializer = _CurrencyCarrierSerializer(data={"currency": "SYP"})

    with django_assert_num_queries(1):
        is_valid = serializer.is_valid()

    assert is_valid, serializer.errors
    assert serializer.validated_data["currency"] == current_syp


def test_field_costs_one_query_per_row(
    active_currency: Currency, deprecated_syp: Currency, current_syp: Currency, django_assert_num_queries
) -> None:
    serializer = _CurrencyCarrierSerializer(
        data=[{"currency": "SYP"}, {"currency": "TST"}, {"currency": "SYP"}], many=True
    )

    with django_assert_num_queries(3):
        is_valid = serializer.is_valid()

    assert is_valid, serializer.errors


def test_field_unknown_code_is_validation_error(django_assert_num_queries) -> None:
    serializer = _CurrencyCarrierSerializer(data={"currency": "MISSING"})

    with django_assert_num_queries(1):
        is_valid = serializer.is_valid()

    assert not is_valid
    assert "currency" in serializer.errors


def test_field_inactive_only_code_is_validation_error(deprecated_syp: Currency, django_assert_num_queries) -> None:
    serializer = _CurrencyCarrierSerializer(data={"currency": "SYP"})

    with django_assert_num_queries(1):
        is_valid = serializer.is_valid()

    assert not is_valid
    assert "currency" in serializer.errors


def test_field_defaults_slug_field_to_code() -> None:
    field = CurrencySlugRelatedField(queryset=Currency.objects.all())

    assert field.slug_field == "code"


def test_field_rejects_an_overridden_slug_field() -> None:
    # Honouring another slug field would make reads use it while writes still resolved
    # by code, so the kwarg is refused outright rather than silently ignored.
    with pytest.raises(TypeError):
        CurrencySlugRelatedField(slug_field="vision_code", queryset=Currency.objects.all())
