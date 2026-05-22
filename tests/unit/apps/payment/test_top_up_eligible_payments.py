from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.models import Payment, PaymentPlan, ProgramCycle

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def cycle(business_area: Any) -> ProgramCycle:
    program = ProgramFactory(business_area=business_area)
    return ProgramCycleFactory(program=program)


@pytest.fixture
def regular_pp(business_area: Any, cycle: ProgramCycle) -> PaymentPlan:
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
    )


@pytest.fixture
def top_up_pp(business_area: Any, cycle: ProgramCycle, regular_pp: PaymentPlan) -> PaymentPlan:
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        source_payment_plan=regular_pp,
    )


@pytest.mark.parametrize(
    "status",
    [
        Payment.STATUS_SUCCESS,
        Payment.STATUS_DISTRIBUTION_SUCCESS,
        Payment.STATUS_DISTRIBUTION_PARTIAL,
        Payment.STATUS_PENDING,
        Payment.STATUS_SENT_TO_PG,
        Payment.STATUS_SENT_TO_FSP,
    ],
)
def test_eligible_payments_for_top_up_arrange_eligible_status_act_query_assert_included(
    regular_pp: PaymentPlan, status: str, django_assert_num_queries: Any
) -> None:
    payment = PaymentFactory(parent=regular_pp, status=status)

    with django_assert_num_queries(1):
        result = list(regular_pp.eligible_payments_for_top_up())

    assert payment in result


@pytest.mark.parametrize(
    "status",
    [
        Payment.STATUS_ERROR,
        Payment.STATUS_FORCE_FAILED,
        Payment.STATUS_MANUALLY_CANCELLED,
        Payment.STATUS_NOT_DISTRIBUTED,
    ],
)
def test_eligible_payments_for_top_up_arrange_failed_status_act_query_assert_excluded(
    regular_pp: PaymentPlan, status: str
) -> None:
    payment = PaymentFactory(parent=regular_pp, status=status)

    result = list(regular_pp.eligible_payments_for_top_up())

    assert payment not in result


def test_eligible_payments_for_top_up_arrange_withdrawn_household_act_query_assert_excluded(
    regular_pp: PaymentPlan,
) -> None:
    payment = PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    payment.household.withdrawn = True
    payment.household.save()

    result = list(regular_pp.eligible_payments_for_top_up())

    assert result == []


def test_eligible_payments_for_top_up_arrange_already_topped_up_act_query_assert_excluded(
    regular_pp: PaymentPlan, top_up_pp: PaymentPlan
) -> None:
    payment = PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    PaymentFactory(parent=top_up_pp, household=payment.household, status=Payment.STATUS_PENDING)

    result = list(regular_pp.eligible_payments_for_top_up())

    assert result == []


def test_eligible_payments_for_top_up_amendment_arrange_delivered_payment_act_query_assert_included(
    top_up_pp: PaymentPlan, django_assert_num_queries: Any
) -> None:
    payment = PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    with django_assert_num_queries(1):
        result = list(top_up_pp.eligible_payments_for_top_up_amendment())

    assert payment in result


@pytest.mark.parametrize(
    "status",
    [Payment.STATUS_PENDING, Payment.STATUS_SENT_TO_PG, Payment.STATUS_SENT_TO_FSP],
)
def test_eligible_payments_for_top_up_amendment_arrange_pending_payment_act_query_assert_excluded(
    top_up_pp: PaymentPlan, status: str
) -> None:
    payment = PaymentFactory(parent=top_up_pp, status=status)

    result = list(top_up_pp.eligible_payments_for_top_up_amendment())

    assert payment not in result


def test_eligible_payments_for_top_up_amendment_arrange_withdrawn_household_act_query_assert_excluded(
    top_up_pp: PaymentPlan,
) -> None:
    payment = PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    payment.household.withdrawn = True
    payment.household.save()

    result = list(top_up_pp.eligible_payments_for_top_up_amendment())

    assert result == []


def test_eligible_payments_for_top_up_amendment_arrange_already_amended_act_query_assert_excluded(
    business_area: Any, cycle: ProgramCycle, top_up_pp: PaymentPlan
) -> None:
    payment = PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    amendment_pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP_AMENDMENT,
        source_payment_plan=top_up_pp,
    )
    PaymentFactory(parent=amendment_pp, household=payment.household, status=Payment.STATUS_PENDING)

    result = list(top_up_pp.eligible_payments_for_top_up_amendment())

    assert result == []
