from pathlib import Path

from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import HopeRecorder

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.periodic_data_update import PDUOnlineEditFactory
from extras.test_utils.factories.program import ProgramFactory

pytestmark = pytest.mark.django_db

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem


@frozenfixture()
def superuser(request, db):
    return UserFactory(is_staff=True, is_superuser=True)


@frozenfixture()
def business_area(request, db):
    return BusinessAreaFactory()


@frozenfixture()
def program(request, db, business_area):
    return ProgramFactory(business_area=business_area)


@frozenfixture()
def role(request, db):
    from hope.apps.account.permissions import Permissions

    return RoleFactory(permissions=[p.value for p in Permissions])


@frozenfixture()
def role_assignment(request, db, superuser, business_area, role):
    return RoleAssignmentFactory(user=superuser, business_area=business_area, role=role)


@frozenfixture()
def pdu_online_edit(request, db, business_area, program, superuser):
    return PDUOnlineEditFactory(business_area=business_area, program=program, created_by=superuser)


def test_list_pdu_online_edits(superuser, business_area, program, role_assignment, pdu_online_edit):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(
        f"/api/rest/business-areas/{business_area.slug}/programs/{program.slug}/periodic-data-update-online-edits/"
    )


def test_retrieve_pdu_online_edit(superuser, business_area, program, role_assignment, pdu_online_edit):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(
        f"/api/rest/business-areas/{business_area.slug}/programs/{program.slug}"
        f"/periodic-data-update-online-edits/{pdu_online_edit.pk}/"
    )
