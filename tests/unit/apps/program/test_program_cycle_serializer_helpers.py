from datetime import date
from unittest.mock import MagicMock

import pytest

from hope.apps.program.api.serializers import ProgramCycleCreateSerializer, ProgramCycleUpdateSerializer


@pytest.fixture
def mock_program():
    return MagicMock()


def test_validate_cycle_start_date_no_program_end_date_valid(mock_program):
    mock_program.start_date = date(2024, 1, 1)
    mock_program.end_date = None

    ProgramCycleCreateSerializer._validate_cycle_start_date(date(2024, 6, 1), mock_program)


def test_parse_program_dates_string_dates(mock_program):
    mock_program.start_date = "2024-01-01"
    mock_program.end_date = "2024-12-31"

    start, end = ProgramCycleUpdateSerializer._parse_program_dates(mock_program)

    assert start == date(2024, 1, 1)
    assert end == date(2024, 12, 31)


def test_parse_program_dates_no_end_date(mock_program):
    mock_program.start_date = "2024-01-01"
    mock_program.end_date = None

    start, end = ProgramCycleUpdateSerializer._parse_program_dates(mock_program)

    assert start == date(2024, 1, 1)
    assert end is None
