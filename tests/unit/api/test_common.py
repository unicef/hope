from django_countries import Countries
import pytest
from rest_framework import serializers

from hope.api.endpoints.rdi.common import DisabilityChoiceField, NullableChoiceField
from hope.apps.household.const import DISABILITY_CHOICES, NOT_DISABLED


@pytest.fixture
def nullable_field() -> NullableChoiceField:
    return NullableChoiceField(
        choices=Countries(),
        required=False,
        allow_blank=True,
    )


@pytest.fixture
def disability_field() -> DisabilityChoiceField:
    return DisabilityChoiceField(
        choices=DISABILITY_CHOICES,
        required=False,
        allow_blank=True,
    )


def test_nullable_blank_converts_to_none(nullable_field: NullableChoiceField) -> None:
    assert nullable_field.to_internal_value("") is None


def test_nullable_valid_choice_passes(nullable_field: NullableChoiceField) -> None:
    code = Countries()[0][0]
    assert nullable_field.to_internal_value(code) == code


def test_nullable_invalid_choice_raises(nullable_field: NullableChoiceField) -> None:
    with pytest.raises(serializers.ValidationError):
        nullable_field.to_internal_value("invalid_value")


def test_disability_blank_converts_to_not_disabled(disability_field: DisabilityChoiceField) -> None:
    assert disability_field.to_internal_value("") == NOT_DISABLED


def test_disability_valid_choice_passes(disability_field: DisabilityChoiceField) -> None:
    code = DISABILITY_CHOICES[0][0]
    assert disability_field.to_internal_value(code) == code


def test_disability_invalid_choice_raises(disability_field: DisabilityChoiceField) -> None:
    with pytest.raises(serializers.ValidationError):
        disability_field.to_internal_value("invalid_choice")
