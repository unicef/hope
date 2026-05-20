"""Tests for RdiXlsxPeopleCreateTask extracted helper methods."""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from hope.apps.registration_data.tasks.rdi_xlsx_people_create import RdiXlsxPeopleCreateTask

pytestmark = pytest.mark.django_db


@pytest.fixture
def people_task():
    with patch.object(RdiXlsxPeopleCreateTask, "__init__", lambda self: None):
        task = RdiXlsxPeopleCreateTask.__new__(RdiXlsxPeopleCreateTask)
        task.index_id = None
        task.households_to_update = []
        task.COMBINED_FIELDS = {}
        task.FLEX_FIELDS = {"individuals": {}, "households": {}}
        task.complex_fields = {"individuals": {}, "households": {}}
        task.complex_types = {}
        task.sheet_title = "individuals"
        task.collectors = {}
        task.households = {}
        task.individuals = []
        return task


@pytest.fixture
def make_cell():
    def _factory(value, row=1):
        cell = MagicMock()
        cell.value = value
        cell.row = row
        return cell

    return _factory


# --- _dispatch_people_field ---


def test_dispatch_people_field_complex_field_branch(people_task, make_cell):
    """When header is in complex_fields, the handler should be called and value set."""
    handler = MagicMock(return_value="processed")
    people_task.complex_fields = {"individuals": {"pp_special": handler}}
    people_task.sheet_title = "individuals"

    cell = make_cell("raw_val", row=5)
    obj = MagicMock()
    current_field = {"name": "target_attr", "required": True}

    people_task._dispatch_people_field("pp_special", cell, "raw_val", current_field, obj)

    handler.assert_called_once_with(
        value="raw_val",
        cell=cell,
        header="pp_special",
        row_num=5,
        individual=obj,
        household=None,
        is_field_required=True,
    )
    assert obj.target_attr == "processed"


def test_dispatch_people_field_complex_field_household_sheet(people_task, make_cell):
    """When sheet_title is households, household kwarg should be obj and individual should be None."""
    handler = MagicMock(return_value="val")
    people_task.complex_fields = {"households": {"pp_hh_field": handler}}
    people_task.sheet_title = "households"

    cell = make_cell("raw", row=3)
    obj = MagicMock()
    current_field = {"name": "attr", "required": False}

    people_task._dispatch_people_field("pp_hh_field", cell, "raw", current_field, obj)

    handler.assert_called_once_with(
        value="raw",
        cell=cell,
        header="pp_hh_field",
        row_num=3,
        individual=None,
        household=obj,
        is_field_required=False,
    )


def test_dispatch_people_field_flex_field_branch(people_task, make_cell):
    """When header is in FLEX_FIELDS, it should process as flex field."""
    people_task.FLEX_FIELDS = {"individuals": {"pp_flex": {"type": "STRING"}}}
    people_task.sheet_title = "individuals"
    people_task.COMBINED_FIELDS = {"pp_flex": {"type": "STRING"}}

    cell = make_cell("flex_val", row=2)
    obj = MagicMock()
    obj.flex_fields = {}

    with patch.object(people_task, "_cast_value", return_value="casted_val"):
        with patch.object(people_task, "_process_flex_field") as mock_process:
            people_task._dispatch_people_field("pp_flex", cell, "flex_val", {"type": "STRING"}, obj)
            mock_process.assert_called_once()


def test_dispatch_people_field_regular_field_branch(people_task, make_cell):
    """When header is not complex and not flex, but obj has the attribute, it should process as regular."""
    people_task.sheet_title = "individuals"
    cell = make_cell("reg_val", row=4)
    obj = MagicMock()
    obj.first_name = "old"
    current_field = {"name": "first_name"}

    with (
        patch.object(people_task, "_cast_value", return_value="casted"),
        patch.object(people_task, "_process_admin_areas_and_country") as mock_admin,
    ):
        people_task._dispatch_people_field("pp_first_name", cell, "reg_val", current_field, obj)
        mock_admin.assert_called_once_with(cell, current_field, "pp_first_name", obj, "casted")


def test_dispatch_people_field_regular_field_skips_none_value(people_task, make_cell):
    """When cast value is None, _process_admin_areas_and_country should NOT be called."""
    people_task.sheet_title = "individuals"
    cell = make_cell(None, row=4)
    obj = MagicMock()
    obj.first_name = "old"
    current_field = {"name": "first_name"}

    with (
        patch.object(people_task, "_cast_value", return_value=None),
        patch.object(people_task, "_process_admin_areas_and_country") as mock_admin,
    ):
        people_task._dispatch_people_field("pp_first_name", cell, None, current_field, obj)
        mock_admin.assert_not_called()


def test_dispatch_people_field_regular_field_skips_empty_string(people_task, make_cell):
    """When cast value is empty string, _process_admin_areas_and_country should NOT be called."""
    people_task.sheet_title = "individuals"
    cell = make_cell("", row=4)
    obj = MagicMock()
    obj.first_name = "old"
    current_field = {"name": "first_name"}

    with (
        patch.object(people_task, "_cast_value", return_value=""),
        patch.object(people_task, "_process_admin_areas_and_country") as mock_admin,
    ):
        people_task._dispatch_people_field("pp_first_name", cell, "", current_field, obj)
        mock_admin.assert_not_called()


# --- _process_people_cell ---


def test_process_people_cell_pdu_column_returns_early(people_task, make_cell):
    """When header is a PDU column, processing should stop immediately."""
    cell = make_cell("val")
    header_cell = make_cell("pdu_field_round_1_value")

    with patch.object(
        type(people_task), "_pdu_column_names", new_callable=PropertyMock, return_value=["pdu_field_round_1_value"]
    ):
        with patch.object(people_task, "_dispatch_people_field") as mock_dispatch:
            people_task._process_people_cell(cell, header_cell, MagicMock())
            mock_dispatch.assert_not_called()


def test_process_people_cell_account_field_prefix_calls_handle_account(people_task, make_cell):
    """When header starts with pp_account__, it should call _handle_account_fields."""
    cell = make_cell("account_val", row=3)
    header_cell = make_cell("pp_account__bank_name")
    obj = MagicMock()

    with patch.object(type(people_task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        with patch.object(people_task, "_handle_account_fields") as mock_handle:
            people_task._process_people_cell(cell, header_cell, obj)
            mock_handle.assert_called_once_with("account_val", "pp_account__bank_name", 3, obj)


def test_process_people_cell_identification_key_sets_value(people_task, make_cell):
    """When header starts with pp_identification_key, it should set identification_key on obj."""
    cell = make_cell("KEY-123")
    header_cell = make_cell("pp_identification_key_1")
    obj = MagicMock()

    with patch.object(type(people_task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        people_task._process_people_cell(cell, header_cell, obj)
        assert obj.identification_key == "KEY-123"


def test_process_people_cell_unknown_field_returns_early(people_task, make_cell):
    """When the header is not in COMBINED_FIELDS or complex_fields, should return early."""
    cell = make_cell("val")
    header_cell = make_cell("pp_unknown_field")

    with patch.object(type(people_task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        with patch.object(people_task, "_dispatch_people_field") as mock_dispatch:
            people_task._process_people_cell(cell, header_cell, MagicMock())
            mock_dispatch.assert_not_called()


def test_process_people_cell_not_required_none_value_non_image_returns_early(people_task, make_cell):
    """When field is not required, value is None, and type is not IMAGE, should return early."""
    people_task.COMBINED_FIELDS = {"pp_optional": {"type": "STRING", "required": False}}
    cell = make_cell(None)
    header_cell = make_cell("pp_optional")

    with patch.object(type(people_task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        with patch.object(people_task, "_dispatch_people_field") as mock_dispatch:
            people_task._process_people_cell(cell, header_cell, MagicMock())
            mock_dispatch.assert_not_called()


def test_process_people_cell_pp_age_returns_early_after_set_index(people_task, make_cell):
    """pp_age header should cause early return after _set_index_id."""
    people_task.COMBINED_FIELDS = {"pp_age": {"type": "INTEGER", "required": True}}
    cell = make_cell("25")
    header_cell = make_cell("pp_age")

    with patch.object(type(people_task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        with patch.object(people_task, "_set_index_id") as mock_set_idx:
            with patch.object(people_task, "_dispatch_people_field") as mock_dispatch:
                people_task._process_people_cell(cell, header_cell, MagicMock())
                mock_set_idx.assert_called_once_with("25", "pp_age")
                mock_dispatch.assert_not_called()


def test_process_people_cell_pp_index_id_returns_early(people_task, make_cell):
    """pp_index_id header should cause early return after _set_index_id."""
    people_task.COMBINED_FIELDS = {"pp_index_id": {"type": "INTEGER", "required": True}}
    cell = make_cell("1")
    header_cell = make_cell("pp_index_id")

    with patch.object(type(people_task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        with patch.object(people_task, "_set_index_id") as mock_set_idx:
            with patch.object(people_task, "_dispatch_people_field") as mock_dispatch:
                people_task._process_people_cell(cell, header_cell, MagicMock())
                mock_set_idx.assert_called_once_with("1", "pp_index_id")
                mock_dispatch.assert_not_called()


def test_process_people_cell_normal_field_calls_dispatch(people_task, make_cell):
    """A normal field that passes all checks should call _dispatch_people_field."""
    people_task.COMBINED_FIELDS = {"pp_first_name": {"type": "STRING", "name": "first_name", "required": True}}
    cell = make_cell("John")
    header_cell = make_cell("pp_first_name")
    obj = MagicMock()

    with patch.object(type(people_task), "_pdu_column_names", new_callable=PropertyMock, return_value=[]):
        with patch.object(people_task, "_set_index_id"):
            with patch.object(people_task, "_dispatch_people_field") as mock_dispatch:
                people_task._process_people_cell(cell, header_cell, obj)
                mock_dispatch.assert_called_once()
                args = mock_dispatch.call_args[0]
                assert args[0] == "pp_first_name"  # header
                assert args[1] == cell  # cell
                assert args[2] == "John"  # cell_value (stripped)
