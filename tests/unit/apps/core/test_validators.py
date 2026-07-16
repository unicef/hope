from unittest.mock import MagicMock, Mock

from django.core.exceptions import ValidationError
import pytest

from hope.apps.core.field_attributes.fields_types import TYPE_INTEGER, TYPE_STRING
from hope.apps.core.validators import BaseValidator, KoboTemplateValidator, prepare_choices_for_validation


def test_base_validator_raises_on_validation_errors():
    class MyValidator(BaseValidator):
        @staticmethod
        def validate_always_fails(*args, **kwargs):
            raise ValidationError("something went wrong")

    with pytest.raises(Exception, match="something went wrong"):
        MyValidator.validate()


def test_prepare_choices_for_validation_missing_list_name_column():
    # Simulate a worksheet with only header columns: name, label
    mock_worksheet = MagicMock()

    # Simulate header row (row 1):
    header_cells = [
        Mock(value="name"),
        Mock(value="label"),
    ]

    # Make worksheet[1] return header row
    mock_worksheet.__getitem__.return_value = header_cells

    # Only header row exists
    mock_worksheet.max_row = 1

    with pytest.raises(ValidationError) as excinfo:
        prepare_choices_for_validation(mock_worksheet)

    assert "Choices sheet does not contain all required columns, missing columns: list_name" in str(excinfo.value)


def test_prepare_choices_for_validation_missing_name_column():
    # Simulate worksheet with missing "name" column
    mock_worksheet = MagicMock()

    # Header row: missing "name"
    mock_worksheet.__getitem__.side_effect = lambda row: {1: [Mock(value="list_name"), Mock(value="label")]}[row]

    mock_worksheet.max_row = 1  # Only header row

    with pytest.raises(ValidationError) as excinfo:
        prepare_choices_for_validation(mock_worksheet)

    assert "Choices sheet does not contain all required columns, missing columns: name" in str(excinfo.value)


def test_prepare_choices_for_validation_missing_both_columns():
    # Simulate worksheet with missing "list_name" and "name"
    mock_worksheet = MagicMock()

    # Header row: neither required column present
    mock_worksheet.__getitem__.side_effect = lambda row: {1: [Mock(value="label"), Mock(value="another_column")]}[row]

    mock_worksheet.max_row = 1

    with pytest.raises(ValidationError) as excinfo:
        prepare_choices_for_validation(mock_worksheet)

    error_message = str(excinfo.value)
    assert "list_name" in error_message
    assert "name" in error_message


def test_prepare_choices_for_validation_all_columns_present():
    # Simulate worksheet with full valid content
    mock_worksheet = MagicMock()

    # Provide rows 1–3
    rows = {
        1: [Mock(value="list_name"), Mock(value="name"), Mock(value="label")],
        2: [Mock(value="Gender"), Mock(value="MALE"), Mock(value="Male")],
        3: [Mock(value="Gender"), Mock(value="FEMALE"), Mock(value="Female")],
    }

    mock_worksheet.__getitem__.side_effect = lambda row: rows[row]
    mock_worksheet.max_row = 3

    result = prepare_choices_for_validation(mock_worksheet)

    assert result == {"Gender": ["MALE", "FEMALE"]}


def test_prepare_choices_for_validation_converts_integer_float_name_to_string():
    mock_worksheet = MagicMock()

    rows = {
        1: [Mock(value="list_name"), Mock(value="name")],
        2: [Mock(value="age_group"), Mock(value=12.0)],
    }

    mock_worksheet.__getitem__.side_effect = lambda row: rows[row]
    mock_worksheet.max_row = 2

    result = prepare_choices_for_validation(mock_worksheet)

    assert result == {"age_group": ["12"]}


def test_map_columns_numbers_missing_required_column_raises():
    first_row = [Mock(value="type"), Mock(value="name")]

    with pytest.raises(ValidationError, match="Survey sheet does not contain all required columns"):
        KoboTemplateValidator._map_columns_numbers(first_row)


def test_get_core_fields_from_file_skips_unknown_field_type():
    mock_worksheet = MagicMock()

    rows = {
        1: [Mock(value="type"), Mock(value="name"), Mock(value="required")],
        2: [Mock(value="barcode"), Mock(value="some_field_i_c"), Mock(value="false")],
    }

    mock_worksheet.__getitem__.side_effect = lambda row: rows[row]
    mock_worksheet.max_row = 2

    result = KoboTemplateValidator._get_core_fields_from_file(mock_worksheet, {}, {"type": 0, "name": 1, "required": 2})

    assert result == {}


def test_check_field_type_mismatch_returns_error():
    result = KoboTemplateValidator._check_field_type("foo_i_c", {"type": TYPE_INTEGER}, TYPE_STRING)

    assert result == {
        "field": "foo_i_c",
        "message": f"Expected type: {TYPE_STRING}, actual type: {TYPE_INTEGER}",
    }


@pytest.mark.django_db
def test_validate_kobo_template_reports_type_mismatch():
    survey_sheet = MagicMock()
    survey_rows = {
        1: [Mock(value="type"), Mock(value="name"), Mock(value="required")],
        2: [Mock(value="integer"), Mock(value="full_name_i_c"), Mock(value="true")],
    }
    survey_sheet.__getitem__.side_effect = lambda row: survey_rows[row]
    survey_sheet.max_row = 2

    choices_sheet = MagicMock()
    choices_rows = {1: [Mock(value="list_name"), Mock(value="name")]}
    choices_sheet.__getitem__.side_effect = lambda row: choices_rows[row]
    choices_sheet.max_row = 1

    errors = KoboTemplateValidator.validate_kobo_template(survey_sheet, choices_sheet)

    assert {
        "field": "full_name_i_c",
        "message": f"Expected type: {TYPE_STRING}, actual type: {TYPE_INTEGER}",
    } in errors
