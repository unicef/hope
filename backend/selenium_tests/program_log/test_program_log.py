import pytest

from hct_mis_api.apps.program.models import Program
from helpers.fixtures import get_program_with_dct_type_and_name

from page_object.program_log.payment_log import ProgramLog

pytestmark = pytest.mark.django_db(transaction=True)

@pytest.fixture
def standard_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "TEST")


@pytest.mark.usefixtures("login")
class TestProgrammeLog:
    def test_smoke_program_log(self, standard_program: Program, pageProgramLog: ProgramLog) -> None:
        pageProgramLog.selectGlobalProgramFilter("Test Program").click()
