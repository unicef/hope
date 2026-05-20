from datetime import timedelta
from decimal import Decimal
from typing import Any
from unittest import mock

from freezegun import freeze_time
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories.household import HouseholdFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory
from hope.apps.payment.celery_tasks import prepare_top_up_payment_plan_async_task
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import Payment, PaymentPlan


@pytest.fixture
def cycle(db):
    return ProgramCycleFactory()


@pytest.fixture
def source_pp(cycle):
    return PaymentPlanFactory(
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        name="Source PP",
    )


@pytest.fixture
def three_eligible_payments(source_pp):
    program = source_pp.program_cycle.program
    business_area = source_pp.business_area
    payments = []
    statuses = [Payment.STATUS_DISTRIBUTION_SUCCESS, Payment.STATUS_PENDING, Payment.STATUS_DISTRIBUTION_PARTIAL]
    for status in statuses:
        household = HouseholdFactory(program=program, business_area=business_area)
        payments.append(PaymentFactory(parent=source_pp, household=household, status=status))
    return payments


@pytest.fixture
def dispersion_dates(source_pp):
    return (
        source_pp.dispersion_start_date + timedelta(days=1),
        source_pp.dispersion_end_date + timedelta(days=1),
    )


@freeze_time("2026-05-15")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_arrange_three_eligible_act_fixed_assert_inherits_attributes(
    get_exchange_rate_mock: Any,
    source_pp,
    three_eligible_payments,
    dispersion_dates,
    django_capture_on_commit_callbacks,
):
    dispersion_start_date, dispersion_end_date = dispersion_dates
    amounts = PaymentPlanService.build_equal_share_amounts(source_pp, Decimal(300))

    top_up_pp = PaymentPlanService(source_pp).create_top_up(
        source_pp.created_by, dispersion_start_date, dispersion_end_date, amounts
    )

    assert top_up_pp.plan_type == PaymentPlan.PlanType.TOP_UP
    assert top_up_pp.source_payment_plan == source_pp
    assert top_up_pp.name == "Source PP Top Up"
    assert top_up_pp.currency == source_pp.currency
    assert top_up_pp.payment_plan_group == source_pp.payment_plan_group
    assert top_up_pp.program_cycle == source_pp.program_cycle
    assert top_up_pp.dispersion_start_date == dispersion_start_date
    assert top_up_pp.dispersion_end_date == dispersion_end_date


@freeze_time("2026-05-15")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_arrange_fixed_act_async_task_assert_payments_equal_share(
    get_exchange_rate_mock: Any,
    source_pp,
    three_eligible_payments,
    dispersion_dates,
    django_capture_on_commit_callbacks,
):
    dispersion_start_date, dispersion_end_date = dispersion_dates
    amounts = PaymentPlanService.build_equal_share_amounts(source_pp, Decimal(300))

    top_up_pp = PaymentPlanService(source_pp).create_top_up(
        source_pp.created_by, dispersion_start_date, dispersion_end_date, amounts
    )
    with django_capture_on_commit_callbacks(execute=True):
        prepare_top_up_payment_plan_async_task(top_up_pp, amounts)
    top_up_pp.refresh_from_db()

    assert top_up_pp.payment_items.count() == 3
    entitlement_quantities = list(top_up_pp.payment_items.values_list("entitlement_quantity", flat=True))
    assert entitlement_quantities == [Decimal("100.00"), Decimal("100.00"), Decimal("100.00")]


@freeze_time("2026-05-15")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_arrange_custom_amounts_act_async_task_assert_skips_zero_amount(
    get_exchange_rate_mock: Any,
    source_pp,
    three_eligible_payments,
    dispersion_dates,
    django_capture_on_commit_callbacks,
):
    dispersion_start_date, dispersion_end_date = dispersion_dates
    amounts = {
        three_eligible_payments[0].household.unicef_id: Decimal("250.00"),
        three_eligible_payments[1].household.unicef_id: Decimal(0),
        three_eligible_payments[2].household.unicef_id: Decimal("75.00"),
    }

    top_up_pp = PaymentPlanService(source_pp).create_top_up(
        source_pp.created_by, dispersion_start_date, dispersion_end_date, amounts
    )
    with django_capture_on_commit_callbacks(execute=True):
        positive = {hh_id: amount for hh_id, amount in amounts.items() if amount > 0}
        prepare_top_up_payment_plan_async_task(top_up_pp, positive)
    top_up_pp.refresh_from_db()

    assert top_up_pp.payment_items.count() == 2
    by_amount = sorted(top_up_pp.payment_items.values_list("entitlement_quantity", flat=True))
    assert by_amount == [Decimal("75.00"), Decimal("250.00")]


@freeze_time("2026-05-15")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_arrange_eligible_act_async_task_assert_source_payment_fk_set(
    get_exchange_rate_mock: Any,
    source_pp,
    three_eligible_payments,
    dispersion_dates,
    django_capture_on_commit_callbacks,
):
    dispersion_start_date, dispersion_end_date = dispersion_dates
    amounts = PaymentPlanService.build_equal_share_amounts(source_pp, Decimal(300))

    top_up_pp = PaymentPlanService(source_pp).create_top_up(
        source_pp.created_by, dispersion_start_date, dispersion_end_date, amounts
    )
    with django_capture_on_commit_callbacks(execute=True):
        prepare_top_up_payment_plan_async_task(top_up_pp, amounts)

    source_payment_ids = set(top_up_pp.payment_items.values_list("source_payment_id", flat=True))
    expected = {p.id for p in three_eligible_payments}
    assert source_payment_ids == expected


@freeze_time("2026-05-15")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_arrange_async_task_act_create_assert_is_follow_up_false(
    get_exchange_rate_mock: Any,
    source_pp,
    three_eligible_payments,
    dispersion_dates,
    django_capture_on_commit_callbacks,
):
    dispersion_start_date, dispersion_end_date = dispersion_dates
    amounts = PaymentPlanService.build_equal_share_amounts(source_pp, Decimal(300))

    top_up_pp = PaymentPlanService(source_pp).create_top_up(
        source_pp.created_by, dispersion_start_date, dispersion_end_date, amounts
    )
    with django_capture_on_commit_callbacks(execute=True):
        prepare_top_up_payment_plan_async_task(top_up_pp, amounts)

    assert top_up_pp.payment_items.filter(is_follow_up=True).count() == 0
    assert top_up_pp.payment_items.filter(is_follow_up=False).count() == 3


def test_create_top_up_arrange_no_eligible_payments_act_create_assert_raises(source_pp, dispersion_dates):
    dispersion_start_date, dispersion_end_date = dispersion_dates

    with pytest.raises(ValidationError) as exc:
        PaymentPlanService(source_pp).create_top_up(
            source_pp.created_by, dispersion_start_date, dispersion_end_date, {}
        )

    assert "no eligible payments" in str(exc.value.detail[0]).lower()


def test_create_top_up_arrange_origin_follow_up_act_create_assert_raises(cycle, dispersion_dates):
    follow_up_pp = PaymentPlanFactory(program_cycle=cycle, plan_type=PaymentPlan.PlanType.FOLLOW_UP)
    dispersion_start_date, dispersion_end_date = dispersion_dates

    with pytest.raises(ValidationError) as exc:
        PaymentPlanService(follow_up_pp).create_top_up(
            follow_up_pp.created_by, dispersion_start_date, dispersion_end_date, {}
        )

    assert "Standard plan" in str(exc.value.detail[0])


def test_create_top_up_arrange_origin_top_up_act_create_assert_raises(cycle, dispersion_dates):
    top_up_pp = PaymentPlanFactory(program_cycle=cycle, plan_type=PaymentPlan.PlanType.TOP_UP)
    dispersion_start_date, dispersion_end_date = dispersion_dates

    with pytest.raises(ValidationError) as exc:
        PaymentPlanService(top_up_pp).create_top_up(
            top_up_pp.created_by, dispersion_start_date, dispersion_end_date, {}
        )

    assert "Standard plan" in str(exc.value.detail[0])


def test_create_top_up_arrange_unknown_household_act_create_assert_raises(
    source_pp, three_eligible_payments, dispersion_dates
):
    dispersion_start_date, dispersion_end_date = dispersion_dates
    amounts = {"HH-NEVER-EXISTED": Decimal(100)}

    with pytest.raises(ValidationError) as exc:
        PaymentPlanService(source_pp).create_top_up(
            source_pp.created_by, dispersion_start_date, dispersion_end_date, amounts
        )

    assert "not eligible" in str(exc.value.detail[0])


def test_create_top_up_arrange_negative_amount_act_create_assert_raises(
    source_pp, three_eligible_payments, dispersion_dates
):
    dispersion_start_date, dispersion_end_date = dispersion_dates
    amounts = {three_eligible_payments[0].household.unicef_id: Decimal(-10)}

    with pytest.raises(ValidationError) as exc:
        PaymentPlanService(source_pp).create_top_up(
            source_pp.created_by, dispersion_start_date, dispersion_end_date, amounts
        )

    assert "non-negative" in str(exc.value.detail[0])


def test_create_top_up_arrange_all_zero_amounts_act_create_assert_raises(
    source_pp, three_eligible_payments, dispersion_dates
):
    dispersion_start_date, dispersion_end_date = dispersion_dates
    amounts = {p.household.unicef_id: Decimal(0) for p in three_eligible_payments}

    with pytest.raises(ValidationError) as exc:
        PaymentPlanService(source_pp).create_top_up(
            source_pp.created_by, dispersion_start_date, dispersion_end_date, amounts
        )

    assert "positive" in str(exc.value.detail[0])


def test_build_equal_share_amounts_arrange_negative_total_act_build_assert_raises(source_pp, three_eligible_payments):
    with pytest.raises(ValidationError) as exc:
        PaymentPlanService.build_equal_share_amounts(source_pp, Decimal(-1))

    assert "greater than 0" in str(exc.value.detail[0])


def test_build_equal_share_amounts_arrange_no_eligible_act_build_assert_raises(source_pp):
    with pytest.raises(ValidationError) as exc:
        PaymentPlanService.build_equal_share_amounts(source_pp, Decimal(100))

    assert "No eligible payments" in str(exc.value.detail[0])


def test_build_equal_share_amounts_arrange_three_eligible_act_build_assert_each_share(
    source_pp, three_eligible_payments
):
    amounts = PaymentPlanService.build_equal_share_amounts(source_pp, Decimal(300))

    assert len(amounts) == 3
    assert set(amounts.values()) == {Decimal("100.00")}


@pytest.mark.parametrize(
    "status",
    [
        Payment.STATUS_DISTRIBUTION_SUCCESS,
        Payment.STATUS_SUCCESS,
        Payment.STATUS_DISTRIBUTION_PARTIAL,
        Payment.STATUS_PENDING,
        Payment.STATUS_SENT_TO_PG,
        Payment.STATUS_SENT_TO_FSP,
    ],
)
def test_create_top_up_parametrized_by_eligible_status_act_create_assert_household_included(
    source_pp, dispersion_dates, status
):
    program = source_pp.program_cycle.program
    business_area = source_pp.business_area
    household = HouseholdFactory(program=program, business_area=business_area)
    PaymentFactory(parent=source_pp, household=household, status=status)
    dispersion_start_date, dispersion_end_date = dispersion_dates

    amounts = PaymentPlanService.build_equal_share_amounts(source_pp, Decimal(50))

    assert household.unicef_id in amounts
    top_up_pp = PaymentPlanService(source_pp).create_top_up(
        source_pp.created_by, dispersion_start_date, dispersion_end_date, amounts
    )
    assert top_up_pp.plan_type == PaymentPlan.PlanType.TOP_UP


@pytest.mark.parametrize(
    "status",
    [
        Payment.STATUS_FORCE_FAILED,
        Payment.STATUS_ERROR,
        Payment.STATUS_MANUALLY_CANCELLED,
        Payment.STATUS_NOT_DISTRIBUTED,
    ],
)
def test_create_top_up_parametrized_by_failed_status_act_create_assert_no_eligible(source_pp, dispersion_dates, status):
    program = source_pp.program_cycle.program
    business_area = source_pp.business_area
    household = HouseholdFactory(program=program, business_area=business_area)
    PaymentFactory(parent=source_pp, household=household, status=status)
    dispersion_start_date, dispersion_end_date = dispersion_dates

    with pytest.raises(ValidationError):
        PaymentPlanService(source_pp).create_top_up(
            source_pp.created_by, dispersion_start_date, dispersion_end_date, {household.unicef_id: Decimal(50)}
        )


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_arrange_already_topped_up_household_act_create_assert_excluded(
    get_exchange_rate_mock: Any,
    source_pp,
    three_eligible_payments,
    dispersion_dates,
    django_capture_on_commit_callbacks,
):
    dispersion_start_date, dispersion_end_date = dispersion_dates
    first_amounts = PaymentPlanService.build_equal_share_amounts(source_pp, Decimal(300))
    first_top_up = PaymentPlanService(source_pp).create_top_up(
        source_pp.created_by, dispersion_start_date, dispersion_end_date, first_amounts
    )
    with django_capture_on_commit_callbacks(execute=True):
        prepare_top_up_payment_plan_async_task(first_top_up, first_amounts)

    with pytest.raises(ValidationError) as exc:
        PaymentPlanService.build_equal_share_amounts(source_pp, Decimal(300))

    assert "No eligible payments" in str(exc.value.detail[0])
