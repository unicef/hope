import pytest

from extras.test_utils.factories import ProgramCycleFactory, ProgramFactory

pytestmark = pytest.mark.django_db


def test_program_factories():
    assert ProgramFactory()
    assert ProgramCycleFactory()
