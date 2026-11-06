"""A Top-Up or an Amendment carrying failed payments can itself be the source of a Follow-Up."""

from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CurrencyFactory,
    PaymentFactory,
    PaymentListFactory,
    PaymentPlanFactory,
    PaymentPlanPurposeFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.payment.services.payment_list_services import PaymentListService
from hope.models import Payment, PaymentList, PaymentPlan, ProgramCycle, User

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
def top_up_with_failed_payment(business_area: Any, cycle: ProgramCycle, purpose: Any) -> PaymentList:
    regular_pp = PaymentListFactory(
        name="Standard PP",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentList.PlanType.REGULAR,
        status=PaymentList.Status.ACCEPTED,
        currency=CurrencyFactory(code="USD"),
        payment_plan_purposes=[purpose],
    )
    top_up = PaymentListFactory(
        name="Standard PP Top Up",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentList.PlanType.TOP_UP,
        status=PaymentList.Status.FINISHED,
        source_payment_list=regular_pp,
        payment_plan=PaymentPlanFactory(
            cycle=cycle,
            plan_type=PaymentList.PlanType.TOP_UP,
            source_payment_plan=regular_pp.payment_plan,
            currency=regular_pp.currency,
        ),
        payment_plan_purposes=[purpose],
    )
    PaymentFactory(parent=top_up, status=Payment.STATUS_ERROR)
    return top_up


def test_can_create_follow_up_arrange_top_up_with_failed_payment_act_get_assert_true(
    top_up_with_failed_payment: PaymentList,
) -> None:
    top_up_group = top_up_with_failed_payment.payment_plan

    assert top_up_group.payment_lists_qualifying_for_linked_payment_plan(PaymentList.PlanType.FOLLOW_UP) == [
        top_up_with_failed_payment
    ]


@pytest.fixture
def follow_up_group_of_top_up(cycle: ProgramCycle, top_up_with_failed_payment: PaymentList) -> PaymentPlan:
    return PaymentPlanFactory(
        cycle=cycle,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        source_payment_plan=top_up_with_failed_payment.payment_plan,
    )


def test_create_follow_up_arrange_top_up_with_failed_payment_act_create_assert_child_of_top_up(
    user: User, top_up_with_failed_payment: PaymentList, follow_up_group_of_top_up: PaymentPlan
) -> None:
    source = top_up_with_failed_payment

    follow_up = PaymentListService(source).create_follow_up(user, payment_plan=follow_up_group_of_top_up)

    assert follow_up.plan_type == PaymentList.PlanType.FOLLOW_UP
    assert follow_up.source_payment_list == source


@pytest.fixture
def amendment_with_failed_payment(top_up_with_failed_payment: PaymentList, purpose: Any) -> PaymentList:
    amendment = PaymentListFactory(
        name="Standard PP Top Up Amendment",
        business_area=top_up_with_failed_payment.business_area,
        program_cycle=top_up_with_failed_payment.program_cycle,
        plan_type=PaymentList.PlanType.TOP_UP_AMENDMENT,
        status=PaymentList.Status.FINISHED,
        source_payment_list=top_up_with_failed_payment,
        payment_plan=PaymentPlanFactory(
            cycle=top_up_with_failed_payment.program_cycle,
            plan_type=PaymentList.PlanType.TOP_UP_AMENDMENT,
            source_payment_plan=top_up_with_failed_payment.payment_plan,
            currency=top_up_with_failed_payment.currency,
        ),
        payment_plan_purposes=[purpose],
    )
    PaymentFactory(parent=amendment, status=Payment.STATUS_ERROR)
    return amendment


def test_can_create_follow_up_arrange_amendment_with_failed_payment_act_get_assert_true(
    amendment_with_failed_payment: PaymentList,
) -> None:
    amendment_group = amendment_with_failed_payment.payment_plan

    assert amendment_group.payment_lists_qualifying_for_linked_payment_plan(PaymentList.PlanType.FOLLOW_UP) == [
        amendment_with_failed_payment
    ]


@pytest.fixture
def follow_up_group_of_amendment(cycle: ProgramCycle, amendment_with_failed_payment: PaymentList) -> PaymentPlan:
    return PaymentPlanFactory(
        cycle=cycle,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        source_payment_plan=amendment_with_failed_payment.payment_plan,
    )


def test_create_follow_up_arrange_amendment_with_failed_payment_act_create_assert_child_of_amendment(
    user: User, amendment_with_failed_payment: PaymentList, follow_up_group_of_amendment: PaymentPlan
) -> None:
    source = amendment_with_failed_payment

    follow_up = PaymentListService(source).create_follow_up(user, payment_plan=follow_up_group_of_amendment)

    assert follow_up.plan_type == PaymentList.PlanType.FOLLOW_UP
    assert follow_up.source_payment_list == source
