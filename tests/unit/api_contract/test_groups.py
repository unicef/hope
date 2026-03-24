from pathlib import Path

from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import HopeRecorder

from extras.test_utils.factories.account import UserFactory

pytestmark = pytest.mark.django_db

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem


@frozenfixture()
def superuser(request, db):
    return UserFactory(is_staff=True, is_superuser=True)


@frozenfixture()
def group(request, db):
    from django.contrib.auth.models import Group, Permission

    g = Group.objects.create(name="Test Group")
    perm = Permission.objects.first()
    if perm:
        g.permissions.add(perm)
    return g


def test_list_groups(superuser, group):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/groups/")


def test_retrieve_group(superuser, group):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(f"/api/rest/groups/{group.pk}/")
