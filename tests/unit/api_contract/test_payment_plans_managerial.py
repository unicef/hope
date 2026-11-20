from pathlib import Path

from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import HopeRecorder

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import PaymentListFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.models.payment_list import PaymentList
from hope.models.payment_plan import PaymentPlan

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
def payment_plan(request, db, program, superuser):
    return PaymentPlanFactory(
        cycle=ProgramCycleFactory(program=program),
        name="Managerial Group",
        status=PaymentPlan.Status.IN_APPROVAL,
        created_by=superuser,
    )


@frozenfixture()
def payment_list(request, db, business_area, program, superuser, payment_plan):
    return PaymentListFactory(
        business_area=business_area,
        program_cycle=payment_plan.cycle,
        payment_plan=payment_plan,
        created_by=superuser,
        status=PaymentList.Status.IN_APPROVAL,
    )


def test_list_payment_plans_managerial(superuser, business_area, program, role_assignment, payment_plan, payment_list):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(f"/api/rest/business-areas/{business_area.slug}/payments/payment-plans-managerial/")
