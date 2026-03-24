from pathlib import Path

from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import HopeRecorder

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import BeneficiaryGroupFactory

pytestmark = pytest.mark.django_db

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem


@frozenfixture()
def superuser(request, db):
    return UserFactory(is_staff=True, is_superuser=True)


@frozenfixture()
def beneficiary_group(request, db):
    return BeneficiaryGroupFactory()


def test_list_beneficiary_groups__returns_expected_fields(superuser, beneficiary_group):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/beneficiary-groups/")
