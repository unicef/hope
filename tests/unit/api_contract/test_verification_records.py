from pathlib import Path

from django.utils import timezone
from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import HopeRecorder

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.models import PaymentPlan

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
def payment_plan(request, db, business_area, program, superuser):
    cycle = ProgramCycleFactory(program=program)
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        created_by=superuser,
        status=PaymentPlan.Status.FINISHED,
    )


@frozenfixture()
def payment_verification_summary(request, db, payment_plan):
    from hope.models.payment_verification_summary import PaymentVerificationSummary

    summary, _ = PaymentVerificationSummary.objects.get_or_create(payment_plan=payment_plan)
    return summary


@frozenfixture()
def payment_verification(request, db, payment_plan, payment_verification_summary):
    verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)
    payment = PaymentFactory(parent=payment_plan)
    return PaymentVerificationFactory(
        payment_verification_plan=verification_plan,
        payment=payment,
        status_date=timezone.now(),
    )


def test_list_verification_records(superuser, business_area, program, role_assignment, payment_verification):
    payment_plan = payment_verification.payment_verification_plan.payment_plan
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(
        f"/api/rest/business-areas/{business_area.slug}/programs/{program.slug}"
        f"/payment-verifications/{payment_plan.pk}/verifications/"
    )


def test_retrieve_verification_record(superuser, business_area, program, role_assignment, payment_verification):
    payment_plan = payment_verification.payment_verification_plan.payment_plan
    payment = payment_verification.payment
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET(
        f"/api/rest/business-areas/{business_area.slug}/programs/{program.slug}"
        f"/payment-verifications/{payment_plan.pk}/verifications/{payment.pk}/"
    )
