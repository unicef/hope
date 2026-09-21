import pytest

from hope.apps.grievance.api.serializers.grievance_ticket import (
    AddIndividualDataSerializer,
    IndividualUpdateDataSerializer,
)

REQUIRED_ADD_DATA = {
    "full_name": "Anna",
    "sex": "FEMALE",
    "birth_date": "1990-01-01",
    "estimated_birth_date": False,
    "relationship": "HEAD",
}


@pytest.mark.parametrize(
    ("serializer_class", "base_data"),
    [(AddIndividualDataSerializer, REQUIRED_ADD_DATA), (IndividualUpdateDataSerializer, {})],
)
@pytest.mark.parametrize(
    "value",
    ["  Anna Kovalska  ", "Anna   Kovalska", "Anna\nKovalska", "Anna\tKovalska", "Anna\xa0Kovalska"],
)
def test_latin_name_field_normalizes_whitespace(serializer_class: type, base_data: dict, value: str) -> None:
    serializer = serializer_class(data={**base_data, "full_name_latin": value})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["full_name_latin"] == "Anna Kovalska"


@pytest.mark.parametrize(
    ("serializer_class", "base_data"),
    [(AddIndividualDataSerializer, REQUIRED_ADD_DATA), (IndividualUpdateDataSerializer, {})],
)
@pytest.mark.parametrize("value", ["Anna--Kovalska", "Anna'''Kovalska", "Anna - ' - Kovalska", "Anna1"])
def test_latin_name_field_rejects_invalid_value(serializer_class: type, base_data: dict, value: str) -> None:
    serializer = serializer_class(data={**base_data, "given_name_latin": value})

    assert not serializer.is_valid()
    assert serializer.errors["given_name_latin"][0].code == "invalid_name"
