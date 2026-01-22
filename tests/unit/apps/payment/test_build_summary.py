import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.models import PaymentVerificationPlan, PaymentVerificationSummary, build_summary

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory(username="test-user", email="test-user@example.com")


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def payment_plan(user, business_area, program_cycle):
    payment_plan = PaymentPlanFactory(
        name="TEST",
        program_cycle=program_cycle,
        business_area=business_area,
        created_by=user,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    return payment_plan


@pytest.fixture
def payment_verification_plan_active(payment_plan):
    return PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        status=PaymentVerificationPlan.STATUS_ACTIVE,
    )


@pytest.fixture
def payment_verification_plan_finished(payment_plan):
    return PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        status=PaymentVerificationPlan.STATUS_FINISHED,
    )


@pytest.fixture
def payment_verification_plan_pending(payment_plan):
    return PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        status=PaymentVerificationPlan.STATUS_PENDING,
    )


def test_status_pending_when_zero_verifications(payment_plan) -> None:
    build_summary(payment_plan)

    summary = payment_plan.payment_verification_summary

    assert summary.status == PaymentVerificationSummary.STATUS_PENDING


def test_status_active_when_at_least_one_active_verification(payment_plan, payment_verification_plan_active) -> None:
    build_summary(payment_plan)

    summary = payment_plan.payment_verification_summary
    assert summary.status == PaymentVerificationSummary.STATUS_ACTIVE


def test_status_finished_when_all_verifications_finished(payment_plan, payment_verification_plan_finished) -> None:
    build_summary(payment_plan)

    summary = payment_plan.payment_verification_summary
    assert summary.status == PaymentVerificationSummary.STATUS_FINISHED


def test_status_pending_when_add_and_removed_verification(payment_plan, payment_verification_plan_pending) -> None:
    payment_verification_plan_pending.delete()

    build_summary(payment_plan)

    summary = payment_plan.payment_verification_summary
    assert summary.status == PaymentVerificationSummary.STATUS_PENDING


def test_query_number(payment_plan, django_assert_num_queries) -> None:
    with django_assert_num_queries(2):
        build_summary(payment_plan)
