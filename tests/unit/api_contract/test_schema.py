from pathlib import Path

from drf_api_checker.pytest import frozenfixture
from drf_api_checker.recorder import HEADERS, STATUS_CODE
import pytest
from unit.api_contract._helpers import HopeRecorder

from extras.test_utils.factories.account import UserFactory

pytestmark = pytest.mark.django_db

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem


@frozenfixture()
def superuser(request, db):
    return UserFactory(is_staff=True, is_superuser=True)


def test_schema__returns_openapi_json(superuser):
    recorder = HopeRecorder(
        DATA_DIR,
        as_user=superuser,
        headers_to_check=["Content-Type", "Allow"],
    )
    recorder.assertGET("/api/rest/", checks=[STATUS_CODE, HEADERS])
