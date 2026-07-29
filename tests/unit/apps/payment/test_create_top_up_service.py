from datetime import timedelta
from decimal import Decimal
from typing import Any
from unittest import mock

from freezegun import freeze_time
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    BusinessAreaFactory,
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
    program = ProgramFactory(business_area=business_area)
    return ProgramCycleFactory(program=program)


@pytest.fixture
def purpose(cycle: ProgramCycle) -> Any:
    p = PaymentPlanPurposeFactory()
    cycle.program.payment_plan_purposes.add(p)
    return p


@pytest.fixture
def regular_pp(business_area: Any, cycle: ProgramCycle, user: User, purpose: Any) -> PaymentPlan:
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        created_by=user,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=PaymentPlan.Status.ACCEPTED,
        name="Test Payment Plan",
        payment_plan_purposes=[purpose],
    )


@pytest.fixture
def source_payments(regular_pp: PaymentPlan) -> dict[str, Payment]:
    return {
        "delivered": PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS),
        "pending": PaymentFactory(parent=regular_pp, status=Payment.STATUS_PENDING),
        "failed": PaymentFactory(parent=regular_pp, status=Payment.STATUS_ERROR),
    }


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_arrange_eligible_payments_act_create_assert_inherits_attributes(
    get_exchange_rate_mock: Any,
    user: User,
    purpose: Any,
    regular_pp: PaymentPlan,
    source_payments: dict[str, Payment],
) -> None:
    start = regular_pp.dispersion_start_date + timedelta(days=1)
    end = regular_pp.dispersion_end_date + timedelta(days=1)

    top_up_pp = PaymentPlanService(regular_pp).create_top_up(user, start, end)

    top_up_pp.refresh_from_db()
    assert top_up_pp.plan_type == PaymentPlan.PlanType.TOP_UP
    assert top_up_pp.status == PaymentPlan.Status.OPEN
    assert top_up_pp.name == "Test Payment Plan Top Up"
    assert top_up_pp.source_payment_plan == regular_pp
    assert top_up_pp.created_by == user
    assert top_up_pp.payment_plan_group == regular_pp.payment_plan_group
    assert top_up_pp.program_cycle == regular_pp.program_cycle
    assert top_up_pp.currency == regular_pp.currency
    assert top_up_pp.financial_service_provider == regular_pp.financial_service_provider
    assert top_up_pp.delivery_mechanism == regular_pp.delivery_mechanism
    assert top_up_pp.dispersion_start_date == start
    assert top_up_pp.dispersion_end_date == end
    assert list(top_up_pp.payment_plan_purposes.values_list("pk", flat=True)) == [purpose.pk]
    assert regular_pp.child_plans.count() == 1


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_arrange_eligible_payments_act_run_task_assert_copies_with_fixed_entitlement(
    get_exchange_rate_mock: Any,
    user: User,
    regular_pp: PaymentPlan,
    source_payments: dict[str, Payment],
    django_capture_on_commit_callbacks: Any,
) -> None:
    """Every source payment is copied whatever its status, funded with the flat amount."""
    start = regular_pp.dispersion_start_date + timedelta(days=1)
    end = regular_pp.dispersion_end_date + timedelta(days=1)
    top_up_pp = PaymentPlanService(regular_pp).create_top_up(user, start, end, fixed_amount=Decimal("15.00"))

    with django_capture_on_commit_callbacks(execute=True):
        prepare_child_payment_plan_async_task(top_up_pp, extra_config={"fixed_amount": "15.00"})

    top_up_pp.refresh_from_db()
    assert set(top_up_pp.payment_items.values_list("source_payment_id", flat=True)) == {
        payment.id for payment in source_payments.values()
    }
    copied = top_up_pp.payment_items.first()
    assert copied.entitlement_quantity == Decimal("15.00")
    assert copied.is_follow_up is False
    assert copied.status == Payment.STATUS_PENDING


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_arrange_query_budget_act_create_assert_within_limit(
    get_exchange_rate_mock: Any,
    user: User,
    regular_pp: PaymentPlan,
    source_payments: dict[str, Payment],
    django_assert_num_queries: Any,
) -> None:
    start = regular_pp.dispersion_start_date + timedelta(days=1)
    end = regular_pp.dispersion_end_date + timedelta(days=1)

    with django_assert_num_queries(10):
        PaymentPlanService(regular_pp).create_top_up(user, start, end)


def test_create_top_up_arrange_follow_up_origin_act_create_assert_raises(
    user: User, business_area: Any, cycle: ProgramCycle
) -> None:
    follow_up_pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    start = follow_up_pp.dispersion_start_date + timedelta(days=1)
    end = follow_up_pp.dispersion_end_date + timedelta(days=1)

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(follow_up_pp).create_top_up(user, start, end)

    assert "Standard plan" in str(error.value.detail[0])


def test_create_top_up_arrange_no_eligible_payments_act_create_assert_raises(
    user: User, regular_pp: PaymentPlan
) -> None:
    # Excluded payments are the remaining way to have none eligible; payment status no longer gates.
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_ERROR, excluded=True)
    start = regular_pp.dispersion_start_date + timedelta(days=1)
    end = regular_pp.dispersion_end_date + timedelta(days=1)

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(regular_pp).create_top_up(user, start, end, fixed_amount=Decimal("5.00"))

    assert "no eligible payments" in str(error.value.detail[0]).lower()
