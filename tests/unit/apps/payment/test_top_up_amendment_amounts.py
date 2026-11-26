"""A Top-Up Amendment is funded at creation exactly like the Top-Up it amends."""

from decimal import Decimal
from typing import Any
from unittest import mock

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
from hope.apps.payment.celery_tasks import prepare_child_payment_list_async_task
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
def top_up_pp(business_area: Any, cycle: ProgramCycle, purpose: Any) -> PaymentList:
    regular_pp = PaymentListFactory(
        name="Standard PP",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentList.PlanType.REGULAR,
        status=PaymentList.Status.ACCEPTED,
        currency=CurrencyFactory(code="USD"),
        payment_plan_purposes=[purpose],
    )
    return PaymentListFactory(
        name="Standard PP Top Up",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentList.PlanType.TOP_UP,
        status=PaymentList.Status.ACCEPTED,
        source_payment_list=regular_pp,
        currency=regular_pp.currency,
        payment_plan_purposes=[purpose],
    )


@pytest.fixture
def amendment_group(cycle: ProgramCycle, top_up_pp: PaymentList) -> PaymentPlan:
    return PaymentPlanFactory(
        cycle=cycle, plan_type=PaymentList.PlanType.TOP_UP_AMENDMENT, source_payment_plan=top_up_pp.payment_plan
    )


@pytest.fixture
def mixed_status_payments(top_up_pp: PaymentList) -> list[Payment]:
    """One of each: delivered, pending, failed. All three are amendable."""
    return [
        PaymentFactory(parent=top_up_pp, status=status)
        for status in (Payment.STATUS_DISTRIBUTION_SUCCESS, Payment.STATUS_PENDING, Payment.STATUS_ERROR)
    ]


def _create_and_run(
    top_up_pp: PaymentList,
    amendment_group: PaymentPlan,
    user: User,
    on_commit: Any,
    *,
    fixed_amount: Decimal | None = None,
    amounts: dict[str, Decimal] | None = None,
) -> PaymentList:
    """Create the Amendment and run the copy job the way the API does."""
    amendment = PaymentListService(top_up_pp).create_top_up_amendment(
        user, payment_plan=amendment_group, fixed_amount=fixed_amount, amounts=amounts
    )
    extra_config = (
        {"amounts": {unicef_id: str(amount) for unicef_id, amount in amounts.items()}}
        if amounts is not None
        else {"fixed_amount": str(fixed_amount)}
    )
    with on_commit(execute=True):
        prepare_child_payment_list_async_task(amendment, extra_config=extra_config)
    amendment.refresh_from_db()
    return amendment


@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=1.0)
def test_create_top_up_amendment_arrange_fixed_amount_act_run_task_assert_every_beneficiary_funded(
    get_exchange_rate_mock: Any,
    user: User,
    top_up_pp: PaymentList,
    mixed_status_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
    amendment_group: Any,
) -> None:
    amendment = _create_and_run(
        top_up_pp, amendment_group, user, django_capture_on_commit_callbacks, fixed_amount=Decimal("30.00")
    )

    assert amendment.payment_items.count() == 3
    assert set(amendment.payment_items.values_list("entitlement_quantity", flat=True)) == {Decimal("30.00")}


@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=1.0)
def test_create_top_up_amendment_arrange_per_beneficiary_amounts_act_run_task_assert_only_listed_funded(
    get_exchange_rate_mock: Any,
    user: User,
    top_up_pp: PaymentList,
    mixed_status_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
    amendment_group: Any,
) -> None:
    funded, *rest = mixed_status_payments

    amendment = _create_and_run(
        top_up_pp,
        amendment_group,
        user,
        django_capture_on_commit_callbacks,
        amounts={funded.unicef_id: Decimal("12.50")},
    )

    assert amendment.payment_items.count() == 1
    copied = amendment.payment_items.first()
    assert copied.source_payment == funded
    assert copied.entitlement_quantity == Decimal("12.50")
    assert set(top_up_pp.eligible_payments_for_top_up_amendment()) == set(rest)


@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=1.0)
def test_create_second_top_up_amendment_arrange_beneficiaries_left_over_act_run_task_assert_disjoint(
    get_exchange_rate_mock: Any,
    user: User,
    top_up_pp: PaymentList,
    mixed_status_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
    amendment_group: Any,
) -> None:
    """A second Amendment picks up exactly the beneficiaries the first one left behind."""
    first_funded, *rest = mixed_status_payments
    first = _create_and_run(
        top_up_pp,
        amendment_group,
        user,
        django_capture_on_commit_callbacks,
        amounts={first_funded.unicef_id: Decimal("12.50")},
    )

    second = _create_and_run(
        top_up_pp, amendment_group, user, django_capture_on_commit_callbacks, fixed_amount=Decimal("5.00")
    )

    assert second.payment_items.count() == 2
    assert set(second.payment_items.values_list("source_payment_id", flat=True)) == {payment.id for payment in rest}
    assert not set(first.payment_items.values_list("household_id", flat=True)) & set(
        second.payment_items.values_list("household_id", flat=True)
    )
    assert top_up_pp.eligible_payments_for_top_up_amendment().count() == 0
