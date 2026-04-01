from unittest.mock import MagicMock

from hope.apps.registration_data.tasks.rdi_xlsx_create import RdiXlsxCreateTask


def test_get_value_returns_none_when_row_is_none() -> None:
    task = RdiXlsxCreateTask.__new__(RdiXlsxCreateTask)
    task.header_index_map = {"name": 0}
    task.row = None

    result = task._get_value("name")

    assert result is None


def test_get_value_returns_cell_value_when_row_exists() -> None:
    task = RdiXlsxCreateTask.__new__(RdiXlsxCreateTask)
    task.header_index_map = {"name": 0}

    cell = MagicMock()
    cell.value = "John"
    task.row = [cell]

    result = task._get_value("name")

    assert result == "John"
