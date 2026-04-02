from unittest.mock import MagicMock

import pytest

from hope.apps.registration_data.tasks.rdi_xlsx_create import RdiXlsxCreateTask


def test_get_value_raises_type_error_when_row_is_none() -> None:
    task = RdiXlsxCreateTask.__new__(RdiXlsxCreateTask)
    task.header_index_map = {"name": 0}
    task.row = None

    with pytest.raises(TypeError):
        task._get_value("name")


def test_get_value_returns_cell_value_when_row_exists() -> None:
    task = RdiXlsxCreateTask.__new__(RdiXlsxCreateTask)
    task.header_index_map = {"name": 0}

    cell = MagicMock()
    cell.value = "John"
    task.row = [cell]

    result = task._get_value("name")

    assert result == "John"
