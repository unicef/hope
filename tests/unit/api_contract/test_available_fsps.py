from pathlib import Path

from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import HopeRecorder

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import DeliveryMechanismFactory, FinancialServiceProviderFactory
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
def delivery_mechanism(request, db):
    return DeliveryMechanismFactory(is_active=True)


@frozenfixture()
def fsp(request, db, business_area, delivery_mechanism):
    fsp = FinancialServiceProviderFactory(delivery_mechanisms=[delivery_mechanism])
    fsp.allowed_business_areas.add(business_area)
    return fsp


def test_available_fsps(superuser, business_area, program, role_assignment, fsp):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    # Drop "Allow" header check — this function-based view returns Allow
    # methods in non-deterministic order across parallel workers.
    recorder.headers_to_check = ["Content-Type"]
    recorder.assertGET(f"/api/rest/business-areas/{business_area.slug}/available-fsps-for-delivery-mechanisms/")
