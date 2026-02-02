import pytest
from pathlib import Path

from django.contrib.auth.models import Group

from drf_api_checker.pytest import frozenfixture

from extras.test_utils.factories.account import UserFactory
from unit.api_contract._helpers import HopeRecorder

pytestmark = pytest.mark.django_db

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem


@pytest.fixture()
def superuser(db):
    return UserFactory(is_staff=True, is_superuser=True)


@frozenfixture()
def group(request, db):
    return Group.objects.create(name="Test Group")


def test_list_groups__returns_expected_fields(superuser, group):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/groups/")


def test_retrieve_group__returns_detail_fields(superuser, group):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(f"/api/rest/groups/{group.pk}/")
