import pytest
from pathlib import Path

from drf_api_checker.pytest import frozenfixture

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.program import ProgramFactory
from unit.api_contract._helpers import HopeRecorder

pytestmark = pytest.mark.django_db

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem


@pytest.fixture()
def superuser(db):
    return UserFactory(is_staff=True, is_superuser=True)


@frozenfixture()
def program(request, db):
    return ProgramFactory()


@pytest.fixture()
def api_token(db, superuser, program):
    from hope.models import APIToken
    from hope.models.utils import Grant

    token = APIToken.objects.create(
        user=superuser,
        grants=[Grant.API_READ_ONLY.name],
    )
    token.valid_for.add(program.business_area)
    return token


def test_list_programs__returns_expected_fields(superuser, api_token, program):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/programs/")
