import pytest

from hope.apps.registration_data.value_caster import SelectOneValueCaster


@pytest.fixture
def caster() -> SelectOneValueCaster:
    return SelectOneValueCaster()


@pytest.fixture
def field() -> dict:
    return {
        "type": "SELECT_ONE",
        "xlsx_field": "test_field",
        "choices": [{"value": "A"}, {"value": "B"}],
    }


def test_process_value_in_choices(caster, field) -> None:
    assert caster.process(field, "A") == "A"


def test_process_value_not_in_choices_converts_to_int(caster, field) -> None:
    assert caster.process(field, "123") == 123


def test_process_value_not_in_choices_returns_string(caster, field) -> None:
    assert caster.process(field, "not_a_number") == "not_a_number"


def test_process_value_with_whitespace(caster, field) -> None:
    assert caster.process(field, "  A  ") == "A"


def test_process_value_uppercase_match(caster, field) -> None:
    field["choices"] = [{"value": "VALID"}]
    assert caster.process(field, "valid") == "VALID"
