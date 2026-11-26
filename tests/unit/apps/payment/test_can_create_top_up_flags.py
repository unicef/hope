from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentFactory,
    PaymentListFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.apps.payment.api.serializers import PaymentPlanDetailSerializer
from hope.models import Payment, PaymentList, PaymentPlan, ProgramCycle

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def cycle(business_area: Any) -> ProgramCycle:
    program = ProgramFactory(business_area=business_area)
    return ProgramCycleFactory(program=program)


@pytest.fixture
def regular_group(cycle: ProgramCycle) -> PaymentPlan:
    return PaymentPlanFactory(cycle=cycle, status=PaymentPlan.Status.ACCEPTED)


@pytest.fixture
def regular_pp(business_area: Any, cycle: ProgramCycle, regular_group: PaymentPlan) -> PaymentList:
    return PaymentListFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan=regular_group,
        plan_type=PaymentList.PlanType.REGULAR,
        status=PaymentList.Status.ACCEPTED,
    )


@pytest.fixture
def top_up_group(cycle: ProgramCycle, regular_group: PaymentPlan) -> PaymentPlan:
    return PaymentPlanFactory(
        cycle=cycle,
        plan_type=PaymentList.PlanType.TOP_UP,
        source_payment_plan=regular_group,
        status=PaymentPlan.Status.ACCEPTED,
    )


@pytest.fixture
def top_up_pp(
    business_area: Any, cycle: ProgramCycle, top_up_group: PaymentPlan, regular_pp: PaymentList
) -> PaymentList:
    return PaymentListFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan=top_up_group,
        plan_type=PaymentList.PlanType.TOP_UP,
        source_payment_list=regular_pp,
        status=PaymentList.Status.ACCEPTED,
    )


@pytest.fixture(params=[1, 25], ids=["one-list", "many-lists"])
def regular_group_with_failed_payments(request: Any, cycle: ProgramCycle, regular_group: PaymentPlan) -> PaymentPlan:
    for _ in range(request.param):
        payment_list = PaymentListFactory(program_cycle=cycle, payment_plan=regular_group)
        PaymentFactory(parent=payment_list, status=Payment.STATUS_ERROR)
    return regular_group


def test_detail_eligibility_flags_have_constant_query_count(
    regular_group_with_failed_payments: PaymentPlan, django_assert_num_queries: Any
) -> None:
    group = regular_group_with_failed_payments

    with django_assert_num_queries(2):
        can_create_follow_up = PaymentPlanDetailSerializer.get_can_create_follow_up(group)
        can_create_top_up = PaymentPlanDetailSerializer.get_can_create_top_up(group)
        can_create_top_up_amendment = PaymentPlanDetailSerializer.get_can_create_top_up_amendment(group)

    assert can_create_follow_up is True
    assert can_create_top_up is True
    assert can_create_top_up_amendment is False


@pytest.fixture(params=[1, 25], ids=["one-top-up-list", "many-top-up-lists"])
def top_up_group_with_pending_payments(
    request: Any, cycle: ProgramCycle, top_up_group: PaymentPlan, regular_pp: PaymentList
) -> PaymentPlan:
    for _ in range(request.param):
        top_up_list = PaymentListFactory(
            program_cycle=cycle,
            payment_plan=top_up_group,
            plan_type=PaymentList.PlanType.TOP_UP,
            source_payment_list=regular_pp,
        )
        PaymentFactory(parent=top_up_list, status=Payment.STATUS_PENDING)
    return top_up_group


def test_amendment_flag_has_constant_query_count(
    top_up_group_with_pending_payments: PaymentPlan, django_assert_num_queries: Any
) -> None:
    group = top_up_group_with_pending_payments

    with django_assert_num_queries(2):
        can_create_follow_up = PaymentPlanDetailSerializer.get_can_create_follow_up(group)
        can_create_top_up = PaymentPlanDetailSerializer.get_can_create_top_up(group)
        can_create_amendment = PaymentPlanDetailSerializer.get_can_create_top_up_amendment(group)

    assert can_create_follow_up is False
    assert can_create_top_up is False
    assert can_create_amendment is True


@pytest.fixture
def regular_group_with_existing_follow_up(regular_group: PaymentPlan, regular_pp: PaymentList) -> PaymentPlan:
    failed_payment = PaymentFactory(parent=regular_pp, status=Payment.STATUS_ERROR)
    follow_up_group = PaymentPlanFactory(
        cycle=regular_pp.program_cycle,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        source_payment_plan=regular_group,
    )
    follow_up_list = PaymentListFactory(
        program_cycle=regular_pp.program_cycle,
        payment_plan=follow_up_group,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        source_payment_list=regular_pp,
    )
    PaymentFactory(
        parent=follow_up_list,
        household=failed_payment.household,
        source_payment=failed_payment,
        is_follow_up=True,
    )
    return regular_group


def test_follow_up_flag_excludes_a_household_already_in_a_follow_up(
    regular_group_with_existing_follow_up: PaymentPlan,
) -> None:
    group = regular_group_with_existing_follow_up

    assert PaymentPlanDetailSerializer.get_can_create_follow_up(group) is False
    assert group.payment_lists_qualifying_for_linked_payment_plan(PaymentList.PlanType.FOLLOW_UP) == []


def test_top_up_arrange_regular_group_with_eligible_payment_act_get_assert_plan_qualifies(
    regular_group: PaymentPlan, regular_pp: PaymentList
) -> None:
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert regular_group.payment_lists_qualifying_for_linked_payment_plan(PaymentList.PlanType.TOP_UP) == [regular_pp]


def test_top_up_arrange_regular_group_without_eligible_payment_act_get_assert_none_qualify(
    regular_group: PaymentPlan, regular_pp: PaymentList
) -> None:
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS, excluded=True)

    assert regular_group.payment_lists_qualifying_for_linked_payment_plan(PaymentList.PlanType.TOP_UP) == []


@pytest.mark.parametrize(
    "status",
    [PaymentPlan.Status.OPEN, PaymentPlan.Status.LOCKED, PaymentPlan.Status.CLOSED],
)
def test_top_up_arrange_group_status_outside_release_window_act_get_assert_none_qualify(
    regular_group: PaymentPlan, regular_pp: PaymentList, status: str
) -> None:
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    regular_group.status = status
    regular_group.save(update_fields=["status"])

    assert regular_group.payment_lists_qualifying_for_linked_payment_plan(PaymentList.PlanType.TOP_UP) == []


def test_top_up_arrange_top_up_group_act_get_assert_none_qualify(
    top_up_group: PaymentPlan, top_up_pp: PaymentList
) -> None:
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert top_up_group.payment_lists_qualifying_for_linked_payment_plan(PaymentList.PlanType.TOP_UP) == []


def test_amendment_arrange_top_up_group_with_delivered_payment_act_get_assert_plan_qualifies(
    top_up_group: PaymentPlan, top_up_pp: PaymentList
) -> None:
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert top_up_group.payment_lists_qualifying_for_linked_payment_plan(PaymentList.PlanType.TOP_UP_AMENDMENT) == [
        top_up_pp
    ]


def test_amendment_arrange_top_up_group_with_only_pending_act_get_assert_plan_qualifies(
    top_up_group: PaymentPlan, top_up_pp: PaymentList
) -> None:
    """A Top-Up group still awaiting delivery can already be amended: payment status does not gate it."""
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_PENDING)

    assert top_up_group.payment_lists_qualifying_for_linked_payment_plan(PaymentList.PlanType.TOP_UP_AMENDMENT) == [
        top_up_pp
    ]


def test_amendment_arrange_top_up_group_without_eligible_payment_act_get_assert_none_qualify(
    top_up_group: PaymentPlan, top_up_pp: PaymentList
) -> None:
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS, excluded=True)

    assert top_up_group.payment_lists_qualifying_for_linked_payment_plan(PaymentList.PlanType.TOP_UP_AMENDMENT) == []


def test_amendment_arrange_regular_group_act_get_assert_none_qualify(
    regular_group: PaymentPlan, regular_pp: PaymentList
) -> None:
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert regular_group.payment_lists_qualifying_for_linked_payment_plan(PaymentList.PlanType.TOP_UP_AMENDMENT) == []
