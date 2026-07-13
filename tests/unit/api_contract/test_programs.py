from pathlib import Path

from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import ProgramsRecorder

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.program import ProgramFactory

pytestmark = pytest.mark.django_db

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem


@frozenfixture()
def superuser(request, db):
    return UserFactory(is_staff=True, is_superuser=True)


@frozenfixture()
def business_area(request, db):
    return BusinessAreaFactory()


@pytest.fixture
def unicef_partner_for_ba(db, business_area):
    """UNICEF subpartner for the business area.

    Kept as a plain (non-frozen) fixture: freezing it stored hard-coded partner
    PKs that, on replay, could be redirected onto an existing ``UNICEF`` row by
    the conftest's unique-name conflict handling, leaving the child's
    ``parent_id`` dangling and poisoning the whole xdist worker at teardown.
    """
    from hope.models import Partner

    unicef, _ = Partner.objects.get_or_create(name="UNICEF")
    partner, _ = Partner.objects.get_or_create(
        name=f"UNICEF Partner for {business_area.slug}",
        defaults={"parent": unicef},
    )
    partner.allowed_business_areas.add(business_area)
    return partner


@pytest.fixture
def partner_role_assignment(db, business_area, unicef_partner_for_ba):
    """RoleAssignment for partner - needed for get_partners query."""
    from hope.apps.core.signals import DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER
    from hope.models import Role, RoleAssignment

    role, _ = Role.objects.get_or_create(
        name="Role for UNICEF Partners",
        is_visible_on_ui=False,
        is_available_for_partner=False,
        defaults={"permissions": DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER},
    )
    ra, _ = RoleAssignment.objects.get_or_create(
        user=None,
        partner=unicef_partner_for_ba,
        role=role,
        business_area=business_area,
        program=None,
    )
    return ra


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


def test_list_programs(superuser, business_area, program, role_assignment, partner_role_assignment):
    recorder = ProgramsRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(f"/api/rest/business-areas/{business_area.slug}/programs/")


def test_retrieve_program(superuser, business_area, program, role_assignment, partner_role_assignment):
    recorder = ProgramsRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(f"/api/rest/business-areas/{business_area.slug}/programs/{program.code}/")
