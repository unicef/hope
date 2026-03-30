from pathlib import Path

from drf_api_checker.pytest import frozenfixture
from drf_api_checker.recorder import STATUS_CODE
import pytest
from unit.api_contract._helpers import HopeRecorder

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
)
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


@frozenfixture()
def other_dm(request, db):
    return DeliveryMechanismFactory(is_active=True, payment_gateway_id="002", code="DM002", name="DM002")


@frozenfixture()
def fsp_with_template(request, db, business_area, delivery_mechanism):
    fsp2 = FinancialServiceProviderFactory(delivery_mechanisms=[delivery_mechanism], name="Other FSP 002")
    fsp2.allowed_business_areas.add(business_area)
    return fsp2


@frozenfixture()
def xlsx_template(request, db, fsp_with_template, other_dm):
    return FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_with_template, delivery_mechanism=other_dm
    )


def test_available_fsps(superuser, business_area, program, role_assignment, fsp):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    # Drop "Allow" header check — this function-based view returns Allow
    # methods in non-deterministic order across parallel workers.
    recorder.headers_to_check = ["Content-Type"]
    recorder.assertGET(f"/api/rest/business-areas/{business_area.slug}/available-fsps-for-delivery-mechanisms/")


def test_available_fsps_empty_resp(
    superuser, business_area, program, role_assignment, fsp_with_template, xlsx_template
):
    # has template but for different delivery mechanism
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.headers_to_check = ["Content-Type"]
    recorder.assertGET(
        f"/api/rest/business-areas/{business_area.slug}/available-fsps-for-delivery-mechanisms/",
        allow_empty=True,
        checks=[STATUS_CODE],
    )
