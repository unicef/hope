"""A Top-Up Amendment is funded at creation exactly like the Top-Up it amends."""

from datetime import timedelta
from decimal import Decimal
from typing import Any
from unittest import mock

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
from hope.apps.payment.celery_tasks import prepare_child_payment_plan_async_task
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
def top_up_pp(business_area: Any, cycle: ProgramCycle, purpose: Any) -> PaymentPlan:
    regular_pp = PaymentPlanFactory(
        name="Standard PP",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=PaymentPlan.Status.ACCEPTED,
        currency=CurrencyFactory(code="USD"),
        payment_plan_purposes=[purpose],
    )
    return PaymentPlanFactory(
        name="Standard PP Top Up",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        status=PaymentPlan.Status.ACCEPTED,
        source_payment_plan=regular_pp,
        currency=regular_pp.currency,
        payment_plan_purposes=[purpose],
    )


@pytest.fixture
def mixed_status_payments(top_up_pp: PaymentPlan) -> list[Payment]:
    """One of each: delivered, pending, failed. All three are amendable."""
    return [
        PaymentFactory(parent=top_up_pp, status=status)
        for status in (Payment.STATUS_DISTRIBUTION_SUCCESS, Payment.STATUS_PENDING, Payment.STATUS_ERROR)
    ]


def _create_and_run(
    top_up_pp: PaymentPlan,
    user: User,
    on_commit: Any,
    *,
    fixed_amount: Decimal | None = None,
    amounts: dict[str, Decimal] | None = None,
) -> PaymentPlan:
    """Create the Amendment and run the copy job the way the API does."""
    start = top_up_pp.dispersion_start_date + timedelta(days=1)
    end = top_up_pp.dispersion_end_date + timedelta(days=1)
    amendment = PaymentPlanService(top_up_pp).create_top_up_amendment(
        user, start, end, fixed_amount=fixed_amount, amounts=amounts
    )
    extra_config = (
        {"amounts": {unicef_id: str(amount) for unicef_id, amount in amounts.items()}}
        if amounts is not None
        else {"fixed_amount": str(fixed_amount)}
    )
    with on_commit(execute=True):
        prepare_child_payment_plan_async_task(amendment, extra_config=extra_config)
    amendment.refresh_from_db()
    return amendment


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0)
def test_create_top_up_amendment_arrange_fixed_amount_act_run_task_assert_every_beneficiary_funded(
    get_exchange_rate_mock: Any,
    user: User,
    top_up_pp: PaymentPlan,
    mixed_status_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
) -> None:
    amendment = _create_and_run(top_up_pp, user, django_capture_on_commit_callbacks, fixed_amount=Decimal("30.00"))

    assert amendment.payment_items.count() == 3
    assert set(amendment.payment_items.values_list("entitlement_quantity", flat=True)) == {Decimal("30.00")}


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0)
def test_create_top_up_amendment_arrange_per_beneficiary_amounts_act_run_task_assert_only_listed_funded(
    get_exchange_rate_mock: Any,
    user: User,
    top_up_pp: PaymentPlan,
    mixed_status_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
) -> None:
    funded, *rest = mixed_status_payments

    amendment = _create_and_run(
        top_up_pp,
        user,
        django_capture_on_commit_callbacks,
        amounts={funded.unicef_id: Decimal("12.50")},
    )

    assert amendment.payment_items.count() == 1
    copied = amendment.payment_items.first()
    assert copied.source_payment == funded
    assert copied.entitlement_quantity == Decimal("12.50")
    assert set(top_up_pp.eligible_payments_for_top_up_amendment()) == set(rest)


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0)
def test_create_second_top_up_amendment_arrange_beneficiaries_left_over_act_run_task_assert_disjoint(
    get_exchange_rate_mock: Any,
    user: User,
    top_up_pp: PaymentPlan,
    mixed_status_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
) -> None:
    """A second Amendment picks up exactly the beneficiaries the first one left behind."""
    first_funded, *rest = mixed_status_payments
    first = _create_and_run(
        top_up_pp,
        user,
        django_capture_on_commit_callbacks,
        amounts={first_funded.unicef_id: Decimal("12.50")},
    )

    second = _create_and_run(top_up_pp, user, django_capture_on_commit_callbacks, fixed_amount=Decimal("5.00"))

    assert second.payment_items.count() == 2
    assert set(second.payment_items.values_list("source_payment_id", flat=True)) == {payment.id for payment in rest}
    assert not set(first.payment_items.values_list("household_id", flat=True)) & set(
        second.payment_items.values_list("household_id", flat=True)
    )
    assert top_up_pp.eligible_payments_for_top_up_amendment().count() == 0
