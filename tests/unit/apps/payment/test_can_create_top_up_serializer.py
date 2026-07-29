from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.apps.payment.api.serializers import PaymentPlanDetailSerializer
from hope.models import Payment, PaymentPlan, ProgramCycle

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def cycle(business_area: Any) -> ProgramCycle:
    program = ProgramFactory(business_area=business_area)
    return ProgramCycleFactory(program=program)


def test_can_create_top_up_arrange_regular_with_eligible_payment_act_get_assert_true(
    business_area: Any, cycle: ProgramCycle
) -> None:
    regular_pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=PaymentPlan.Status.ACCEPTED,
    )
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert PaymentPlanDetailSerializer().get_can_create_top_up(regular_pp) is True


def test_can_create_top_up_arrange_regular_without_eligible_payment_act_get_assert_false(
    business_area: Any, cycle: ProgramCycle
) -> None:
    regular_pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=PaymentPlan.Status.ACCEPTED,
    )
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS, excluded=True)

    assert PaymentPlanDetailSerializer().get_can_create_top_up(regular_pp) is False


@pytest.mark.parametrize(
    "status",
    [PaymentPlan.Status.OPEN, PaymentPlan.Status.LOCKED, PaymentPlan.Status.CLOSED],
)
def test_can_create_top_up_arrange_status_outside_release_window_act_get_assert_false(
    business_area: Any, cycle: ProgramCycle, status: str
) -> None:
    regular_pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=status,
    )
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert PaymentPlanDetailSerializer().get_can_create_top_up(regular_pp) is False


@pytest.mark.parametrize(
    "plan_type",
    [
        PaymentPlan.PlanType.TOP_UP,
        PaymentPlan.PlanType.FOLLOW_UP,
        PaymentPlan.PlanType.TOP_UP_AMENDMENT,
    ],
)
def test_can_create_top_up_arrange_non_regular_plan_act_get_assert_false(
    business_area: Any, cycle: ProgramCycle, plan_type: str
) -> None:
    plan = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=plan_type,
        status=PaymentPlan.Status.ACCEPTED,
    )
    PaymentFactory(parent=plan, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert PaymentPlanDetailSerializer().get_can_create_top_up(plan) is False


def test_can_create_top_up_amendment_arrange_top_up_with_delivered_payment_act_get_assert_true(
    business_area: Any, cycle: ProgramCycle
) -> None:
    top_up_pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        status=PaymentPlan.Status.ACCEPTED,
    )
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert PaymentPlanDetailSerializer().get_can_create_top_up_amendment(top_up_pp) is True


def test_can_create_top_up_amendment_arrange_top_up_with_only_pending_act_get_assert_true(
    business_area: Any, cycle: ProgramCycle
) -> None:
    """A Top-Up still awaiting delivery can already be amended: status does not gate it."""
    top_up_pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        status=PaymentPlan.Status.ACCEPTED,
    )
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_PENDING)

    assert PaymentPlanDetailSerializer().get_can_create_top_up_amendment(top_up_pp) is True


def test_can_create_top_up_amendment_arrange_top_up_without_eligible_payment_act_get_assert_false(
    business_area: Any, cycle: ProgramCycle
) -> None:
    top_up_pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        status=PaymentPlan.Status.ACCEPTED,
    )
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS, excluded=True)

    assert PaymentPlanDetailSerializer().get_can_create_top_up_amendment(top_up_pp) is False


@pytest.mark.parametrize(
    "plan_type",
    [
        PaymentPlan.PlanType.REGULAR,
        PaymentPlan.PlanType.FOLLOW_UP,
        PaymentPlan.PlanType.TOP_UP_AMENDMENT,
    ],
)
def test_can_create_top_up_amendment_arrange_non_top_up_plan_act_get_assert_false(
    business_area: Any, cycle: ProgramCycle, plan_type: str
) -> None:
    plan = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=plan_type,
        status=PaymentPlan.Status.ACCEPTED,
    )
    PaymentFactory(parent=plan, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert PaymentPlanDetailSerializer().get_can_create_top_up_amendment(plan) is False
