"""A Top-Up or an Amendment carrying failed payments can itself be the source of a Follow-Up."""

from datetime import timedelta
from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CurrencyFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanPurposeFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.payment.api.serializers import PaymentPlanDetailSerializer
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import Payment, PaymentPlan, ProgramCycle, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def cycle(business_area: Any) -> ProgramCycle:
    return ProgramCycleFactory(program=ProgramFactory(business_area=business_area))


@pytest.fixture
def purpose(cycle: ProgramCycle) -> Any:
    p = PaymentPlanPurposeFactory()
    cycle.program.payment_plan_purposes.add(p)
    return p


@pytest.fixture
def top_up_with_failed_payment(business_area: Any, cycle: ProgramCycle, purpose: Any) -> PaymentPlan:
    regular_pp = PaymentPlanFactory(
        name="Standard PP",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=PaymentPlan.Status.ACCEPTED,
        currency=CurrencyFactory(code="USD"),
        payment_plan_purposes=[purpose],
    )
    top_up = PaymentPlanFactory(
        name="Standard PP Top Up",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        status=PaymentPlan.Status.FINISHED,
        source_payment_plan=regular_pp,
        currency=regular_pp.currency,
        payment_plan_purposes=[purpose],
    )
    PaymentFactory(parent=top_up, status=Payment.STATUS_ERROR)
    return top_up


def test_can_create_follow_up_arrange_top_up_with_failed_payment_act_get_assert_true(
    top_up_with_failed_payment: PaymentPlan,
) -> None:
    assert PaymentPlanDetailSerializer().get_can_create_follow_up(top_up_with_failed_payment) is True


def test_create_follow_up_arrange_top_up_with_failed_payment_act_create_assert_child_of_top_up(
    user: User, top_up_with_failed_payment: PaymentPlan
) -> None:
    source = top_up_with_failed_payment
    start = source.dispersion_start_date + timedelta(days=1)
    end = source.dispersion_end_date + timedelta(days=1)

    follow_up = PaymentPlanService(source).create_follow_up(user, start, end)

    assert follow_up.plan_type == PaymentPlan.PlanType.FOLLOW_UP
    assert follow_up.source_payment_plan == source


@pytest.fixture
def amendment_with_failed_payment(top_up_with_failed_payment: PaymentPlan, purpose: Any) -> PaymentPlan:
    amendment = PaymentPlanFactory(
        name="Standard PP Top Up Amendment",
        business_area=top_up_with_failed_payment.business_area,
        program_cycle=top_up_with_failed_payment.program_cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP_AMENDMENT,
        status=PaymentPlan.Status.FINISHED,
        source_payment_plan=top_up_with_failed_payment,
        currency=top_up_with_failed_payment.currency,
        payment_plan_purposes=[purpose],
    )
    PaymentFactory(parent=amendment, status=Payment.STATUS_ERROR)
    return amendment


def test_can_create_follow_up_arrange_amendment_with_failed_payment_act_get_assert_true(
    amendment_with_failed_payment: PaymentPlan,
) -> None:
    assert PaymentPlanDetailSerializer().get_can_create_follow_up(amendment_with_failed_payment) is True


def test_create_follow_up_arrange_amendment_with_failed_payment_act_create_assert_child_of_amendment(
    user: User, amendment_with_failed_payment: PaymentPlan
) -> None:
    source = amendment_with_failed_payment
    start = source.dispersion_start_date + timedelta(days=1)
    end = source.dispersion_end_date + timedelta(days=1)

    follow_up = PaymentPlanService(source).create_follow_up(user, start, end)

    assert follow_up.plan_type == PaymentPlan.PlanType.FOLLOW_UP
    assert follow_up.source_payment_plan == source
