from unittest.mock import MagicMock

import pytest

from hope.apps.program.api.serializers import ProgramCycleUpdateSerializer


def test_parse_program_dates_raises_when_start_date_is_unparseable():
    program = MagicMock()
    program.start_date = "not-a-date"
    program.end_date = None
    with pytest.raises(ValueError, match="program_start_date must not be None"):
        ProgramCycleUpdateSerializer._parse_program_dates(program)
