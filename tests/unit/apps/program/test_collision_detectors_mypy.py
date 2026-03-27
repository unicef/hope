import pytest

from extras.test_utils.factories import ProgramFactory
from hope.apps.program.collision_detectors import IdentificationKeyCollisionDetector
from hope.models import Household

pytestmark = pytest.mark.django_db


@pytest.fixture()
def program():
    return ProgramFactory()


def test_detect_collision_returns_none_for_null_identification_key(program):
    detector = IdentificationKeyCollisionDetector(program)
    household = Household(identification_key=None)
    assert detector.detect_collision(household) is None
