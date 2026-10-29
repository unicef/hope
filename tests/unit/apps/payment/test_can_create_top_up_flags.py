from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.models import Payment, PaymentPlan, PaymentPlanGroup, ProgramCycle

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def cycle(business_area: Any) -> ProgramCycle:
    program = ProgramFactory(business_area=business_area)
    return ProgramCycleFactory(program=program)


@pytest.fixture
def regular_group(cycle: ProgramCycle) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(cycle=cycle, status=PaymentPlanGroup.Status.ACCEPTED)


@pytest.fixture
def regular_pp(business_area: Any, cycle: ProgramCycle, regular_group: PaymentPlanGroup) -> PaymentPlan:
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=regular_group,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=PaymentPlan.Status.ACCEPTED,
    )


@pytest.fixture
def top_up_group(cycle: ProgramCycle, regular_group: PaymentPlanGroup) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(
        cycle=cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        source_group=regular_group,
        status=PaymentPlanGroup.Status.ACCEPTED,
    )


@pytest.fixture
def top_up_pp(
    business_area: Any, cycle: ProgramCycle, top_up_group: PaymentPlanGroup, regular_pp: PaymentPlan
) -> PaymentPlan:
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=top_up_group,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        source_payment_plan=regular_pp,
        status=PaymentPlan.Status.ACCEPTED,
    )


def test_top_up_arrange_regular_group_with_eligible_payment_act_get_assert_plan_qualifies(
    regular_group: PaymentPlanGroup, regular_pp: PaymentPlan
) -> None:
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert regular_group.plans_qualifying_for_linked_group(PaymentPlan.PlanType.TOP_UP) == [regular_pp]


def test_top_up_arrange_regular_group_without_eligible_payment_act_get_assert_none_qualify(
    regular_group: PaymentPlanGroup, regular_pp: PaymentPlan
) -> None:
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS, excluded=True)

    assert regular_group.plans_qualifying_for_linked_group(PaymentPlan.PlanType.TOP_UP) == []


@pytest.mark.parametrize(
    "status",
    [PaymentPlanGroup.Status.OPEN, PaymentPlanGroup.Status.LOCKED, PaymentPlanGroup.Status.CLOSED],
)
def test_top_up_arrange_group_status_outside_release_window_act_get_assert_none_qualify(
    regular_group: PaymentPlanGroup, regular_pp: PaymentPlan, status: str
) -> None:
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    regular_group.status = status
    regular_group.save(update_fields=["status"])

    assert regular_group.plans_qualifying_for_linked_group(PaymentPlan.PlanType.TOP_UP) == []


def test_top_up_arrange_top_up_group_act_get_assert_none_qualify(
    top_up_group: PaymentPlanGroup, top_up_pp: PaymentPlan
) -> None:
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert top_up_group.plans_qualifying_for_linked_group(PaymentPlan.PlanType.TOP_UP) == []


def test_amendment_arrange_top_up_group_with_delivered_payment_act_get_assert_plan_qualifies(
    top_up_group: PaymentPlanGroup, top_up_pp: PaymentPlan
) -> None:
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert top_up_group.plans_qualifying_for_linked_group(PaymentPlan.PlanType.TOP_UP_AMENDMENT) == [top_up_pp]


def test_amendment_arrange_top_up_group_with_only_pending_act_get_assert_plan_qualifies(
    top_up_group: PaymentPlanGroup, top_up_pp: PaymentPlan
) -> None:
    """A Top-Up group still awaiting delivery can already be amended: payment status does not gate it."""
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_PENDING)

    assert top_up_group.plans_qualifying_for_linked_group(PaymentPlan.PlanType.TOP_UP_AMENDMENT) == [top_up_pp]


def test_amendment_arrange_top_up_group_without_eligible_payment_act_get_assert_none_qualify(
    top_up_group: PaymentPlanGroup, top_up_pp: PaymentPlan
) -> None:
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS, excluded=True)

    assert top_up_group.plans_qualifying_for_linked_group(PaymentPlan.PlanType.TOP_UP_AMENDMENT) == []


def test_amendment_arrange_regular_group_act_get_assert_none_qualify(
    regular_group: PaymentPlanGroup, regular_pp: PaymentPlan
) -> None:
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert regular_group.plans_qualifying_for_linked_group(PaymentPlan.PlanType.TOP_UP_AMENDMENT) == []
