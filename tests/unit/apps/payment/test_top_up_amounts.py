from datetime import timedelta
from decimal import Decimal
import logging
from typing import Any
from unittest import mock

from django.contrib.contenttypes.models import ContentType
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
def source_pp(business_area: Any, cycle: ProgramCycle, purpose: Any) -> PaymentPlan:
    return PaymentPlanFactory(
        name="Standard PP",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=PaymentPlan.Status.ACCEPTED,
        currency=CurrencyFactory(code="USD"),
        payment_plan_purposes=[purpose],
    )


@pytest.fixture
def three_payments(source_pp: PaymentPlan) -> list[Payment]:
    return [PaymentFactory(parent=source_pp, status=Payment.STATUS_PENDING) for _ in range(3)]


def _create_and_run(
    source_pp: PaymentPlan,
    user: User,
    on_commit: Any,
    *,
    fixed_amount: Decimal | None = None,
    amounts: dict[str, Decimal] | None = None,
) -> PaymentPlan:
    """Create the Top-Up and run the copy job the way the API does.

    The job is kicked off explicitly rather than through the on_commit hook so the amounts the
    endpoint resolved travel with it, mirroring what `create_top_up` queues in production.
    """
    start = source_pp.dispersion_start_date + timedelta(days=1)
    end = source_pp.dispersion_end_date + timedelta(days=1)
    top_up = PaymentPlanService(source_pp).create_top_up(user, start, end, fixed_amount=fixed_amount, amounts=amounts)
    extra_config = (
        {"fixed_amount": str(fixed_amount)}
        if amounts is None
        else {"amounts": {unicef_id: str(amount) for unicef_id, amount in amounts.items()}}
    )
    with on_commit(execute=True):
        prepare_child_payment_plan_async_task(top_up, extra_config=extra_config)
    top_up.refresh_from_db()
    return top_up


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0)
def test_create_top_up_arrange_fixed_amount_act_run_task_assert_every_beneficiary_funded(
    get_exchange_rate_mock: Any,
    user: User,
    source_pp: PaymentPlan,
    three_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
) -> None:
    top_up = _create_and_run(source_pp, user, django_capture_on_commit_callbacks, fixed_amount=Decimal("25.00"))

    assert top_up.payment_items.count() == 3
    assert set(top_up.payment_items.values_list("entitlement_quantity", flat=True)) == {Decimal("25.00")}


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0)
def test_create_top_up_arrange_per_beneficiary_amounts_act_run_task_assert_only_funded_copied(
    get_exchange_rate_mock: Any,
    user: User,
    source_pp: PaymentPlan,
    three_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
) -> None:
    funded, _skipped, also_funded = three_payments
    amounts = {funded.unicef_id: Decimal("10.00"), also_funded.unicef_id: Decimal("30.00")}

    top_up = _create_and_run(source_pp, user, django_capture_on_commit_callbacks, amounts=amounts)

    assert top_up.payment_items.count() == 2
    assert dict(top_up.payment_items.values_list("source_payment__unicef_id", "entitlement_quantity")) == amounts


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0)
def test_create_top_up_arrange_beneficiary_left_out_act_check_eligibility_assert_still_available(
    get_exchange_rate_mock: Any,
    user: User,
    source_pp: PaymentPlan,
    three_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
) -> None:
    funded, skipped, _other = three_payments
    _create_and_run(
        source_pp,
        user,
        django_capture_on_commit_callbacks,
        amounts={funded.unicef_id: Decimal("10.00")},
    )

    still_eligible = source_pp.eligible_payments_for_top_up()

    assert skipped in still_eligible
    assert funded not in still_eligible


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0)
def test_create_top_up_arrange_beneficiary_already_topped_up_act_exclude_them_assert_still_blocked(
    get_exchange_rate_mock: Any,
    user: User,
    source_pp: PaymentPlan,
    three_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
) -> None:
    """Excluding someone from a Top-Up must not recycle them into the eligible pool.

    Selection happens through the amount file at creation time; exclusion afterwards is a
    different operation and must not double as a second way of freeing a beneficiary.
    """
    funded = three_payments[0]
    top_up = _create_and_run(
        source_pp,
        user,
        django_capture_on_commit_callbacks,
        amounts={funded.unicef_id: Decimal("10.00")},
    )
    top_up.payment_items.update(excluded=True)

    assert funded not in source_pp.eligible_payments_for_top_up()


def test_eligible_payments_for_top_up_arrange_withdrawn_household_act_query_assert_not_eligible(
    source_pp: PaymentPlan,
) -> None:
    payment = PaymentFactory(parent=source_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    payment.household.withdrawn = True
    payment.household.save(update_fields=["withdrawn"])

    assert payment not in source_pp.eligible_payments_for_top_up()


@pytest.mark.parametrize(
    "status",
    [PaymentPlan.Status.OPEN, PaymentPlan.Status.LOCKED, PaymentPlan.Status.IN_REVIEW, PaymentPlan.Status.CLOSED],
)
def test_create_top_up_arrange_source_outside_accepted_or_finished_act_create_assert_raises(
    user: User,
    source_pp: PaymentPlan,
    three_payments: list[Payment],
    status: str,
) -> None:
    source_pp.status = status
    source_pp.save(update_fields=["status"])
    start = source_pp.dispersion_start_date + timedelta(days=1)
    end = source_pp.dispersion_end_date + timedelta(days=1)

    with pytest.raises(Exception, match="Accepted or Finished"):
        PaymentPlanService(source_pp).create_top_up(user, start, end, fixed_amount=Decimal("5.00"))


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0)
def test_create_top_up_arrange_finished_source_act_create_assert_top_up_created(
    get_exchange_rate_mock: Any,
    user: User,
    source_pp: PaymentPlan,
    three_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
) -> None:
    source_pp.status = PaymentPlan.Status.FINISHED
    source_pp.save(update_fields=["status"])

    top_up = _create_and_run(source_pp, user, django_capture_on_commit_callbacks, fixed_amount=Decimal("25.00"))

    assert top_up.plan_type == PaymentPlan.PlanType.TOP_UP
    assert top_up.payment_items.count() == 3


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0)
def test_create_top_up_arrange_second_top_up_for_remaining_act_run_task_assert_disjoint_beneficiaries(
    get_exchange_rate_mock: Any,
    user: User,
    source_pp: PaymentPlan,
    three_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
) -> None:
    first_payment, second_payment, third_payment = three_payments
    first_top_up = _create_and_run(
        source_pp,
        user,
        django_capture_on_commit_callbacks,
        amounts={first_payment.unicef_id: Decimal("10.00")},
    )
    second_top_up = _create_and_run(
        source_pp,
        user,
        django_capture_on_commit_callbacks,
        amounts={second_payment.unicef_id: Decimal("20.00")},
    )

    assert list(first_top_up.payment_items.values_list("source_payment_id", flat=True)) == [first_payment.id]
    assert list(second_top_up.payment_items.values_list("source_payment_id", flat=True)) == [second_payment.id]
    assert third_payment in source_pp.eligible_payments_for_top_up()


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0)
def test_create_top_up_arrange_fixed_amount_act_run_task_assert_query_count(
    get_exchange_rate_mock: Any,
    user: User,
    source_pp: PaymentPlan,
    three_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
    django_assert_num_queries: Any,
) -> None:
    start = source_pp.dispersion_start_date + timedelta(days=1)
    end = source_pp.dispersion_end_date + timedelta(days=1)
    # Django never clears this between tests, so without it the count depends on what ran before.
    ContentType.objects.clear_cache()

    with django_assert_num_queries(71), django_capture_on_commit_callbacks(execute=True):
        PaymentPlanService(source_pp).create_top_up(user, start, end, fixed_amount=Decimal("25.00"))


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0)
def test_create_top_up_arrange_beneficiary_claimed_between_validation_and_copy_act_run_task_assert_shrink_logged(
    get_exchange_rate_mock: Any,
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    source_pp: PaymentPlan,
    three_payments: list[Payment],
    django_capture_on_commit_callbacks: Any,
    caplog: Any,
) -> None:
    """A beneficiary claimed by a sibling Top-Up after validation is skipped, but never silently."""
    claimed, funded, _other = three_payments
    amounts = {claimed.unicef_id: Decimal("10.00"), funded.unicef_id: Decimal("30.00")}
    start = source_pp.dispersion_start_date + timedelta(days=1)
    end = source_pp.dispersion_end_date + timedelta(days=1)
    top_up = PaymentPlanService(source_pp).create_top_up(user, start, end, amounts=amounts)
    competing_pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        source_payment_plan=source_pp,
    )
    PaymentFactory(parent=competing_pp, household=claimed.household, status=Payment.STATUS_PENDING)

    with (
        caplog.at_level(logging.WARNING),
        django_capture_on_commit_callbacks(execute=True),
    ):
        prepare_child_payment_plan_async_task(
            top_up, extra_config={"amounts": {unicef_id: str(amount) for unicef_id, amount in amounts.items()}}
        )

    top_up.refresh_from_db()
    assert list(top_up.payment_items.values_list("source_payment__unicef_id", flat=True)) == [funded.unicef_id]
    assert claimed.unicef_id in caplog.text
