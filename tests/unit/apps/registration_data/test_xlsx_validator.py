import io

from openpyxl import Workbook
import pytest

from hope.apps.registration_data.validators import XlsxError, XLSXValidator


def _xlsx_file(name: str = "good.xlsx") -> io.BytesIO:
    buffer = io.BytesIO()
    Workbook().save(buffer)
    buffer.seek(0)
    buffer.name = name
    return buffer


def test_xlsx_error_stores_errors() -> None:
    errors = [{"row_number": 1, "header": "h", "message": "m"}]

    assert XlsxError(errors).errors == errors


def test_validate_file_extension_rejects_non_xlsx() -> None:
    bad = io.BytesIO(b"a,b,c")
    bad.name = "data.csv"

    result = XLSXValidator.validate_file_extension(file=bad)

    assert result[0]["message"] == "Only .xlsx files are accepted for import"


def test_validate_file_extension_accepts_valid_xlsx() -> None:
    assert XLSXValidator.validate_file_extension(file=_xlsx_file()) == []


def test_validate_file_extension_rejects_corrupt_xlsx() -> None:
    corrupt = io.BytesIO(b"not really a zip")
    corrupt.name = "broken.xlsx"

    result = XLSXValidator.validate_file_extension(file=corrupt)

    assert result[0]["message"] == "Invalid .xlsx file"


def test_validate_file_extension_reraises_on_missing_file() -> None:
    with pytest.raises(KeyError):
        XLSXValidator.validate_file_extension()


def test_validate_raises_xlsx_error_when_a_method_returns_errors() -> None:
    bad = io.BytesIO(b"a,b,c")
    bad.name = "data.csv"

    with pytest.raises(XlsxError) as exc_info:
        XLSXValidator.validate(file=bad)

    assert exc_info.value.errors[0]["message"] == "Only .xlsx files are accepted for import"


def test_validate_passes_for_valid_file() -> None:
    assert XLSXValidator.validate(file=_xlsx_file()) is None
