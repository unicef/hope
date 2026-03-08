from pathlib import Path

from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import HopeRecorder

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.payment import AccountTypeFactory
from extras.test_utils.factories.program import ProgramFactory

pytestmark = pytest.mark.django_db

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem


@frozenfixture()
def superuser(request, db):
    return UserFactory(is_staff=True, is_superuser=True)


@frozenfixture()
def business_area(request, db):
    ba = BusinessAreaFactory(code="BA9000", slug="business-area-9000", name="Business Area Contract")
    ba.countries.add(
        CountryFactory(name="Testland", short_name="Testland", iso_code2="TL", iso_code3="TLN", iso_num="9999")
    )
    return ba


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
def account_type(request, db):
    return AccountTypeFactory(unique_fields=["account_number"])


def test_list_business_areas(superuser, business_area, program, role_assignment):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/business-areas/")


def test_retrieve_business_area(superuser, business_area, program, role_assignment):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(f"/api/rest/business-areas/{business_area.slug}/")


def test_all_collector_fields_attributes(superuser, business_area, program, role_assignment, account_type):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/business-areas/all-collector-fields-attributes/")


def test_all_fields_attributes(superuser, business_area, program, role_assignment):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(f"/api/rest/business-areas/{business_area.slug}/all-fields-attributes/")
