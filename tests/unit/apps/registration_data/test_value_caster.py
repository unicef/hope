from datetime import date, datetime

import pytest

from hope.apps.registration_data.value_caster import (
    BooleanValueCaster,
    DateValueCaster,
    DecimalValueCaster,
    DefaultValueCaster,
    IntegerValueCaster,
    SelectManyValueCaster,
    SelectOneValueCaster,
    StringValueCaster,
)


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


def test_cast_processes_when_can_process() -> None:
    caster = StringValueCaster()

    assert caster.cast({"type": "STRING"}, 5) == "5"


def test_cast_delegates_to_next_caster_when_cannot_process() -> None:
    chain = IntegerValueCaster(next_caster=StringValueCaster())

    assert chain.cast({"type": "STRING"}, "hello") == "hello"


# --- StringValueCaster ---


def test_string_caster_converts_integer_float_without_decimal() -> None:
    assert StringValueCaster().process({"type": "STRING"}, 5.0) == "5"


def test_string_caster_keeps_non_integer_float() -> None:
    assert StringValueCaster().process({"type": "STRING"}, 5.5) == "5.5"


def test_string_caster_can_process() -> None:
    assert StringValueCaster().can_process({"type": "STRING"}) is True
    assert StringValueCaster().can_process({"type": "INTEGER"}) is False


# --- IntegerValueCaster / DecimalValueCaster ---


def test_integer_caster_casts_to_int() -> None:
    assert IntegerValueCaster().process({"type": "INTEGER"}, "42") == 42


def test_decimal_caster_casts_to_float() -> None:
    assert DecimalValueCaster().process({"type": "DECIMAL"}, "4.2") == 4.2


# --- SelectManyValueCaster ---


@pytest.fixture
def many_field() -> dict:
    return {"type": "SELECT_MANY", "xlsx_field": "f", "choices": [{"value": "A"}, {"value": "B"}]}


def test_select_many_custom_cast_value_used(many_field) -> None:
    many_field["custom_cast_value"] = lambda input_value: ["X"]

    assert SelectManyValueCaster().process(many_field, "ignored") == ["X"]


def test_select_many_splits_on_comma(many_field) -> None:
    assert SelectManyValueCaster().process(many_field, "A,B") == ["A", "B"]


def test_select_many_splits_on_semicolon(many_field) -> None:
    assert SelectManyValueCaster().process(many_field, "A;B") == ["A", "B"]


def test_select_many_splits_on_space_and_matches_uppercase(many_field) -> None:
    assert SelectManyValueCaster().process(many_field, "a b") == ["A", "B"]


def test_select_many_unknown_numeric_becomes_int(many_field) -> None:
    assert SelectManyValueCaster().process(many_field, "1,2") == [1, 2]


def test_select_many_unknown_non_numeric_kept_as_string(many_field) -> None:
    assert SelectManyValueCaster().process(many_field, "C,D") == ["C", "D"]


# --- SelectOneValueCaster extra branches ---


def test_select_one_custom_cast_value_used(field) -> None:
    field["custom_cast_value"] = lambda input_value: "custom"

    assert SelectOneValueCaster().process(field, "A") == "custom"


def test_select_one_integer_float_field_suffix_stringified(field) -> None:
    field["xlsx_field"] = "score_i_f"
    field["choices"] = [{"value": "5"}]

    assert SelectOneValueCaster().process(field, 5.0) == "5"


def test_select_one_returns_none_when_value_is_non_string_choice() -> None:
    field = {"type": "SELECT_ONE", "xlsx_field": "f", "choices": [{"value": 1}]}

    assert SelectOneValueCaster().process(field, 1) is None


# --- DateValueCaster ---


def test_date_caster_passes_through_date() -> None:
    today = date(2024, 1, 1)

    assert DateValueCaster().process({"type": "DATE"}, today) is today


def test_date_caster_parses_string() -> None:
    assert DateValueCaster().process({"type": "DATE"}, "2024-01-02") == datetime(2024, 1, 2)


def test_date_caster_returns_none_for_unsupported_type() -> None:
    assert DateValueCaster().process({"type": "DATE"}, 12345) is None


# --- BooleanValueCaster ---


@pytest.mark.parametrize(
    ("value", "expected"),
    [("false", False), ("TRUE", True), ("0", False), ("1", True), ("maybe", "maybe"), (True, True)],
)
def test_boolean_caster(value: object, expected: object) -> None:
    assert BooleanValueCaster().process({"type": "BOOL"}, value) == expected


# --- DefaultValueCaster ---


@pytest.mark.parametrize(
    ("caster", "field_type"),
    [
        (IntegerValueCaster(), "INTEGER"),
        (DecimalValueCaster(), "DECIMAL"),
        (SelectManyValueCaster(), "SELECT_MANY"),
        (SelectOneValueCaster(), "SELECT_ONE"),
        (DateValueCaster(), "DATE"),
        (BooleanValueCaster(), "BOOL"),
    ],
)
def test_can_process_matches_only_its_type(caster, field_type: str) -> None:
    assert caster.can_process({"type": field_type}) is True
    assert caster.can_process({"type": "OTHER"}) is False


def test_default_caster_can_always_process_and_returns_value() -> None:
    caster = DefaultValueCaster()

    assert caster.can_process({"type": "anything"}) is True
    assert caster.process({"type": "anything"}, "value") == "value"
