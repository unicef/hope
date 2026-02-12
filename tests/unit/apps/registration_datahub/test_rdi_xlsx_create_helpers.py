"""Tests for RdiXlsxCreateTask extracted helper methods."""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from hope.apps.registration_datahub.tasks.rdi_xlsx_create import RdiXlsxCreateTask

pytestmark = pytest.mark.django_db


@pytest.fixture
def task():
    return RdiXlsxCreateTask()


def _make_header_cells(names: list[str]) -> list:
    cells = []
    for name in names:
        cell = MagicMock()
        cell.value = name
        cells.append(cell)
    return cells


# --- _find_header_indices ---


def test_find_header_indices_both_present(task):
    first_row = _make_header_cells(["name", "household_id", "age", "relationship_i_c"])
    hh_idx, rel_idx = task._find_header_indices(first_row)
    assert hh_idx == 1
    assert rel_idx == 3


def test_find_header_indices_none_present(task):
    first_row = _make_header_cells(["name", "age", "sex"])
    hh_idx, rel_idx = task._find_header_indices(first_row)
    assert hh_idx is None
    assert rel_idx is None


def test_find_header_indices_only_household_id(task):
    first_row = _make_header_cells(["household_id", "name"])
    hh_idx, rel_idx = task._find_header_indices(first_row)
    assert hh_idx == 0
    assert rel_idx is None


# --- _should_skip_cell ---


def test_should_skip_cell_pdu_column(task):
    with patch.object(
        type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=["pdu_field_round_1_value"]
    ):
        result = task._should_skip_cell(
            "pdu_field_round_1_value", "val", {"type": "STRING"}, {"individuals": {}}, "individuals"
        )
    assert result is True


def test_should_skip_cell_excluded_age(task):
    with patch.object(type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        result = task._should_skip_cell("age", "25", {"type": "INTEGER"}, {"individuals": {}}, "individuals")
    assert result is True


def test_should_skip_cell_not_in_field_or_complex(task):
    with patch.object(type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        result = task._should_skip_cell("unknown_header", "val", {}, {"individuals": {}}, "individuals")
    assert result is True


def test_should_skip_cell_not_required_empty_non_image(task):
    with patch.object(type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        result = task._should_skip_cell(
            "some_field",
            None,
            {"type": "STRING", "required": False},
            {"individuals": {"some_field": lambda **kw: None}},
            "individuals",
        )
    assert result is True


def test_should_skip_cell_required_field_not_skipped(task):
    with patch.object(type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        result = task._should_skip_cell(
            "some_field", "value", {"type": "STRING", "required": True}, {"individuals": {}}, "individuals"
        )
    assert result is False


def test_should_skip_cell_image_type_not_skipped_when_empty(task):
    with patch.object(type(task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        result = task._should_skip_cell(
            "photo_field", None, {"type": "IMAGE", "required": False}, {"individuals": {}}, "individuals"
        )
    assert result is False


# --- _process_complex_field ---


def test_process_complex_field_not_in_complex_fields(task):
    result = task._process_complex_field(
        "regular_field", "value", MagicMock(), MagicMock(), {"individuals": {}}, "individuals", {}, {}
    )
    assert result is False


def test_process_complex_field_calls_handler_and_sets_attr(task):
    handler = MagicMock(return_value="processed_value")
    obj = MagicMock()
    cell = MagicMock()
    cell.row = 5

    complex_fields = {"individuals": {"special_field": handler}}
    combined_fields = {"special_field": {"name": "target_attr"}}
    current_field = {"required": True}

    result = task._process_complex_field(
        "special_field", "raw_value", cell, obj, complex_fields, "individuals", current_field, combined_fields
    )
    assert result is True
    handler.assert_called_once()
    assert obj.target_attr == "processed_value"


def test_process_complex_field_handler_returns_none_no_setattr(task):
    handler = MagicMock(return_value=None)
    obj = MagicMock(spec=[])  # no attributes
    cell = MagicMock()
    cell.row = 5

    complex_fields = {"individuals": {"field": handler}}
    combined_fields = {"field": {"name": "attr"}}

    result = task._process_complex_field("field", "val", cell, obj, complex_fields, "individuals", {}, combined_fields)
    assert result is True
    assert not hasattr(obj, "attr")


# --- _process_regular_field ---


def test_process_regular_field_household_id_returns_false(task):
    obj = MagicMock()
    combined_fields = {"household_id": {"name": "household_id"}}
    result = task._process_regular_field("household_id", "val", MagicMock(), obj, combined_fields)
    assert result is False


def test_process_regular_field_no_attribute_returns_false(task):
    obj = MagicMock(spec=[])
    combined_fields = {"some_field": {"name": "nonexistent_attr"}}
    result = task._process_regular_field("some_field", "val", MagicMock(), obj, combined_fields)
    assert result is False


def test_process_regular_field_none_value_returns_true(task):
    obj = MagicMock()
    obj.some_attr = "old"
    combined_fields = {"some_field": {"name": "some_attr"}}
    with patch.object(task, "_cast_value", return_value=None):
        result = task._process_regular_field("some_field", None, MagicMock(), obj, combined_fields)
    assert result is True


# --- _create_pending_object_factory ---


def test_create_pending_object_factory_households(task):
    from extras.test_utils.factories import RegistrationDataImportFactory

    rdi = RegistrationDataImportFactory()
    factory = task._create_pending_object_factory("households", rdi)
    assert callable(factory)


def test_create_pending_object_factory_individuals(task):
    from extras.test_utils.factories import RegistrationDataImportFactory

    rdi = RegistrationDataImportFactory()
    factory = task._create_pending_object_factory("individuals", rdi)
    assert callable(factory)


def test_create_pending_object_factory_invalid_raises(task):
    rdi = MagicMock()
    with pytest.raises(ValueError, match="Unhandled sheet label"):
        task._create_pending_object_factory("invalid_sheet", rdi)
