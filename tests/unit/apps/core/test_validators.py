from unittest.mock import MagicMock, Mock

from django.core.exceptions import ValidationError
import pytest

from hope.apps.core.validators import prepare_choices_for_validation


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
