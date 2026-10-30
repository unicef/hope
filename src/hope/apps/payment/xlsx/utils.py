from openpyxl.worksheet.worksheet import Worksheet


def get_last_data_row(ws: Worksheet) -> int:
    """Return the last row holding a value, ignoring trailing styled-but-empty cells.

    ``ws.max_row`` also counts formatted empty cells, and
    ``ws.iter_rows()`` creates and stores a Cell for every coordinate it visits, so iterating up to
    ``max_row`` can materialise millions of cells. openpyxl has no public API to find the last
    row with a value without iterating, hence the read of the already-parsed ``ws._cells``.
    """
    return max((row for (row, _column), cell in ws._cells.items() if cell.value is not None), default=1)
