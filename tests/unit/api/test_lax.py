from unittest.mock import MagicMock

import pytest

from hope.api.endpoints.rdi.lax import CreateLaxBaseView


def test_rdi_program_raises_when_program_is_none():
    view = CreateLaxBaseView.__new__(CreateLaxBaseView)
    mock_rdi = MagicMock()
    mock_rdi.program = None
    view.selected_rdi = mock_rdi

    with pytest.raises(ValueError, match="RDI program must not be None"):
        _ = view._rdi_program
