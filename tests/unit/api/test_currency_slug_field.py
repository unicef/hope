from django.core.exceptions import ImproperlyConfigured
import pytest
from rest_framework import serializers

from extras.test_utils.factories import CurrencyFactory
from hope.api.utils import CurrencySlugRelatedField, OnUnchangedCode
from hope.models.currency import Currency

pytestmark = pytest.mark.django_db


class _CreateCarrierSerializer(serializers.Serializer):
    currency = CurrencySlugRelatedField(on_unchanged_code=OnUnchangedCode.ALWAYS_ACTIVE, allow_null=True)


class _UpdateCarrierSerializer(serializers.Serializer):
    currency = CurrencySlugRelatedField(on_unchanged_code=OnUnchangedCode.KEEP_CURRENT_ROW, allow_null=True)


@pytest.fixture
def active_currency() -> Currency:
    return CurrencyFactory(code="TST", name="Test", vision_code="TST", active=True)


@pytest.fixture
def deprecated_syp() -> Currency:
    return CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=False)


@pytest.fixture
def current_syp() -> Currency:
    return CurrencyFactory(code="SYP", name="Syrian pound", vision_code="SYP01", active=True)


@pytest.fixture
def retired_with_vision_code() -> Currency:
    return CurrencyFactory(code="VEF", name="Venezuelan bolivar", vision_code="VEF01", active=False)


def test_field_resolves_active_currency(active_currency: Currency, django_assert_num_queries) -> None:
    serializer = _CreateCarrierSerializer(data={"currency": "TST"})

    with django_assert_num_queries(1):
        is_valid = serializer.is_valid()

    assert is_valid, serializer.errors
    assert serializer.validated_data["currency"] == active_currency


def test_field_resolves_active_row_for_shared_code(
    deprecated_syp: Currency, current_syp: Currency, django_assert_num_queries
) -> None:
    serializer = _CreateCarrierSerializer(data={"currency": "SYP"})

    with django_assert_num_queries(1):
        is_valid = serializer.is_valid()

    assert is_valid, serializer.errors
    assert serializer.validated_data["currency"] == current_syp


def test_field_costs_one_query_per_row(
    active_currency: Currency, deprecated_syp: Currency, current_syp: Currency, django_assert_num_queries
) -> None:
    serializer = _CreateCarrierSerializer(
        data=[{"currency": "SYP"}, {"currency": "TST"}, {"currency": "SYP"}], many=True
    )

    with django_assert_num_queries(3):
        is_valid = serializer.is_valid()

    assert is_valid, serializer.errors


def test_field_unknown_code_is_validation_error(django_assert_num_queries) -> None:
    serializer = _CreateCarrierSerializer(data={"currency": "MISSING"})

    with django_assert_num_queries(3):
        is_valid = serializer.is_valid()

    assert not is_valid
    assert "currency" in serializer.errors


def test_field_inactive_only_code_is_validation_error(deprecated_syp: Currency, django_assert_num_queries) -> None:
    serializer = _CreateCarrierSerializer(data={"currency": "SYP"})

    with django_assert_num_queries(2):
        is_valid = serializer.is_valid()

    assert not is_valid
    assert "currency" in serializer.errors


def test_field_resolves_the_vision_code_alias_to_the_active_row(
    deprecated_syp: Currency, current_syp: Currency, django_assert_num_queries
) -> None:
    serializer = _CreateCarrierSerializer(data={"currency": "SYP01"})

    with django_assert_num_queries(3):
        is_valid = serializer.is_valid()

    assert is_valid, serializer.errors
    assert serializer.validated_data["currency"] == current_syp


def test_field_inactive_only_alias_is_validation_error(retired_with_vision_code: Currency) -> None:
    serializer = _CreateCarrierSerializer(data={"currency": "VEF01"})

    assert not serializer.is_valid()
    assert serializer.errors["currency"][0].code == "does_not_exist"


def test_field_represents_a_currency_by_code_after_resolving_the_alias(
    deprecated_syp: Currency, current_syp: Currency
) -> None:
    serializer = _CreateCarrierSerializer(data={"currency": "SYP01"})
    serializer.is_valid()

    assert serializer.data == {"currency": "SYP"}


def test_field_moves_an_update_that_sends_the_alias_onto_the_active_row(
    deprecated_syp: Currency, current_syp: Currency
) -> None:
    # The alias is a different code from the deprecated row's, so it is a deliberate change.
    instance = type("_Carrier", (), {"currency": deprecated_syp})()
    serializer = _UpdateCarrierSerializer(instance, data={"currency": "SYP01"})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["currency"] == current_syp


def test_field_keeps_the_deprecated_row_an_update_echoes_back(
    deprecated_syp: Currency, current_syp: Currency, django_assert_num_queries
) -> None:
    instance = type("_Carrier", (), {"currency": deprecated_syp})()
    serializer = _UpdateCarrierSerializer(instance, data={"currency": "SYP"})

    with django_assert_num_queries(0):
        is_valid = serializer.is_valid()

    assert is_valid, serializer.errors
    assert serializer.validated_data["currency"] == deprecated_syp


def test_field_resolves_to_active_row_when_an_update_changes_the_code(
    active_currency: Currency, deprecated_syp: Currency, current_syp: Currency
) -> None:
    instance = type("_Carrier", (), {"currency": active_currency})()
    serializer = _UpdateCarrierSerializer(instance, data={"currency": "SYP"})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["currency"] == current_syp


def test_field_refuses_keep_current_row_without_the_instance(active_currency: Currency) -> None:
    serializer = _UpdateCarrierSerializer(data={"currency": "TST"})

    with pytest.raises(ImproperlyConfigured):
        serializer.is_valid()


def test_field_defaults_slug_field_to_code() -> None:
    field = CurrencySlugRelatedField(on_unchanged_code=OnUnchangedCode.ALWAYS_ACTIVE)

    assert field.slug_field == "code"


@pytest.mark.parametrize("kwarg", ["slug_field", "queryset"])
def test_field_rejects_kwargs_that_would_imply_they_steer_validation(kwarg: str) -> None:
    with pytest.raises(TypeError):
        CurrencySlugRelatedField(on_unchanged_code=OnUnchangedCode.ALWAYS_ACTIVE, **{kwarg: Currency.objects.all()})


def test_field_requires_an_explicit_unchanged_code_mode() -> None:
    # No safe default: the modes differ exactly in the case this field exists for.
    with pytest.raises(TypeError):
        CurrencySlugRelatedField(allow_null=True)


class _WildcardSerializer(serializers.Serializer):
    """KEEP_CURRENT_ROW cannot find the instance behind ``source="*"``."""

    currency = CurrencySlugRelatedField(on_unchanged_code=OnUnchangedCode.KEEP_CURRENT_ROW, source="*")


class _DottedSourceSerializer(serializers.Serializer):
    """Nor behind a dotted source."""

    currency = CurrencySlugRelatedField(on_unchanged_code=OnUnchangedCode.KEEP_CURRENT_ROW, source="household.currency")


def test_field_rejects_keep_current_row_on_a_wildcard_source() -> None:
    with pytest.raises(ImproperlyConfigured):
        _WildcardSerializer().fields  # noqa: B018


def test_field_rejects_keep_current_row_on_a_dotted_source() -> None:
    with pytest.raises(ImproperlyConfigured):
        _DottedSourceSerializer().fields  # noqa: B018


def test_field_rejects_keep_current_row_with_many_true(active_currency: Currency) -> None:
    serializer = _UpdateCarrierSerializer([], data=[{"currency": "TST"}], many=True)

    with pytest.raises(ImproperlyConfigured):
        serializer.is_valid()


def test_field_nul_byte_is_validation_error_not_a_driver_error(active_currency: Currency) -> None:
    serializer = _CreateCarrierSerializer(data={"currency": "TS\x00T"})

    assert not serializer.is_valid()
    assert serializer.errors["currency"][0].code == "invalid"
    assert "\x00" not in str(serializer.errors["currency"][0])


def test_field_non_string_value_is_validation_error(active_currency: Currency) -> None:
    serializer = _CreateCarrierSerializer(data={"currency": {"code": "TST"}})

    assert not serializer.is_valid()
    assert "currency" in serializer.errors
