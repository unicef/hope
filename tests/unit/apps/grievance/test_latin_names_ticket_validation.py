from typing import Any

import pytest

from hope.apps.grievance.api.serializers.grievance_ticket import (
    AddIndividualDataSerializer,
    IndividualUpdateDataSerializer,
)


@pytest.fixture
def add_individual_payload() -> dict[str, Any]:
    return {
        "full_name": "Анна Ковальська",
        "sex": "FEMALE",
        "birth_date": "1990-01-01",
        "estimated_birth_date": False,
        "relationship": "HEAD",
    }


@pytest.mark.parametrize(
    ("extra", "is_valid"),
    [
        ({"transliterate_latin_names": True}, True),
        ({"full_name_latin": "Anna Kovalska"}, True),
        ({}, False),
        ({"transliterate_latin_names": False}, False),
    ],
)
def test_add_individual_requires_latin_or_transliteration_flag(
    add_individual_payload: dict[str, Any], extra: dict[str, Any], is_valid: bool
) -> None:
    serializer = AddIndividualDataSerializer(data={**add_individual_payload, **extra})

    assert serializer.is_valid() is is_valid
    if not is_valid:
        assert "full_name_latin" in str(serializer.errors)


@pytest.mark.parametrize(
    ("data", "is_valid"),
    [
        ({"given_name": "Анна", "transliterate_latin_names": True}, True),
        ({"given_name": "Анна", "given_name_latin": "Anna"}, True),
        ({"given_name": "Анна"}, False),
        ({"given_name": "Анна", "full_name_latin": "Anna"}, False),
        ({"phone_no": "+48123123123"}, True),
        ({}, True),
    ],
)
def test_individual_update_requires_latin_or_transliteration_flag(data: dict[str, Any], is_valid: bool) -> None:
    serializer = IndividualUpdateDataSerializer(data=data)

    assert serializer.is_valid() is is_valid
    if not is_valid:
        assert "given_name_latin" in str(serializer.errors)
