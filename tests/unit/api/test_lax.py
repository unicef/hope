from unittest.mock import MagicMock

from hope.api.endpoints.rdi.lax import CreateLaxBaseView


def test_rdi_program_returns_program_of_selected_rdi():
    view = CreateLaxBaseView.__new__(CreateLaxBaseView)
    program = MagicMock()
    mock_rdi = MagicMock()
    mock_rdi.program = program
    view.selected_rdi = mock_rdi

    assert view._rdi_program is program
