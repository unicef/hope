import pytest

from extras.test_utils.old_factories.core import create_afghanistan
from extras.test_utils.old_factories.program import ProgramFactory
from hope.models import Program

pytestmark = pytest.mark.django_db


class TestProgramManager:
    def test_get_by_unicef_id_returns_program(self) -> None:
        business_area = create_afghanistan()
        program = ProgramFactory(business_area=business_area, programme_code="AB12")

        result = Program.objects.get_by_unicef_id(f"{business_area.slug}-{program.programme_code.lower()}")

        assert result == program

    def test_get_by_unicef_id_not_found(self) -> None:
        create_afghanistan()

        with pytest.raises(Program.DoesNotExist) as exc_info:
            Program.objects.get_by_unicef_id("missing-id")

        assert str(exc_info.value) == "Program matching unicef_id 'missing-id' does not exist."
