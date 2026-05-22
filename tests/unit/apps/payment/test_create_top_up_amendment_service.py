from datetime import timedelta
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
from hope.apps.payment.celery_tasks import prepare_top_up_payment_plan_async_task
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
def purpose(business_area: Any) -> Any:
    return PaymentPlanPurposeFactory(business_area=business_area)


@pytest.fixture
def regular_pp(business_area: Any, cycle: ProgramCycle) -> PaymentPlan:
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
    )


@pytest.fixture
def top_up_pp(
    business_area: Any,
    cycle: ProgramCycle,
    user: User,
    purpose: Any,
    regular_pp: PaymentPlan,
) -> PaymentPlan:
    pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        created_by=user,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        source_payment_plan=regular_pp,
        name="Test Plan Top Up",
    )
    pp.payment_plan_purposes.add(purpose)
    return pp


@pytest.fixture
def top_up_payments(top_up_pp: PaymentPlan) -> dict[str, Payment]:
    return {
        "delivered": PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS),
        "pending": PaymentFactory(parent=top_up_pp, status=Payment.STATUS_PENDING),
    }


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_amendment_arrange_eligible_payments_act_create_assert_inherits_attributes(
    get_exchange_rate_mock: Any,
    user: User,
    purpose: Any,
    top_up_pp: PaymentPlan,
    top_up_payments: dict[str, Payment],
) -> None:
    start = top_up_pp.dispersion_start_date + timedelta(days=1)
    end = top_up_pp.dispersion_end_date + timedelta(days=1)

    amendment_pp = PaymentPlanService(top_up_pp).create_top_up_amendment(user, start, end)

    amendment_pp.refresh_from_db()
    assert amendment_pp.plan_type == PaymentPlan.PlanType.TOP_UP_AMENDMENT
    assert amendment_pp.status == PaymentPlan.Status.OPEN
    assert amendment_pp.name == "Test Plan Top Up Amendment"
    assert amendment_pp.source_payment_plan == top_up_pp
    assert amendment_pp.payment_plan_group == top_up_pp.payment_plan_group
    assert amendment_pp.currency == top_up_pp.currency
    assert list(amendment_pp.payment_plan_purposes.values_list("pk", flat=True)) == [purpose.pk]
    assert top_up_pp.child_plans.count() == 1


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_amendment_arrange_eligible_payments_act_run_task_assert_copies_only_delivered(
    get_exchange_rate_mock: Any,
    user: User,
    top_up_pp: PaymentPlan,
    top_up_payments: dict[str, Payment],
    django_capture_on_commit_callbacks: Any,
) -> None:
    start = top_up_pp.dispersion_start_date + timedelta(days=1)
    end = top_up_pp.dispersion_end_date + timedelta(days=1)
    amendment_pp = PaymentPlanService(top_up_pp).create_top_up_amendment(user, start, end)

    with django_capture_on_commit_callbacks(execute=True):
        prepare_top_up_payment_plan_async_task(amendment_pp, "create_top_up_amendment_payments")

    amendment_pp.refresh_from_db()
    assert amendment_pp.payment_items.count() == 1
    copied = amendment_pp.payment_items.first()
    assert copied.source_payment == top_up_payments["delivered"]
    assert copied.entitlement_quantity is None
    assert copied.entitlement_quantity_usd is None
    assert copied.is_follow_up is False


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_amendment_arrange_query_budget_act_create_assert_within_limit(
    get_exchange_rate_mock: Any,
    user: User,
    top_up_pp: PaymentPlan,
    top_up_payments: dict[str, Payment],
    django_assert_num_queries: Any,
) -> None:
    start = top_up_pp.dispersion_start_date + timedelta(days=1)
    end = top_up_pp.dispersion_end_date + timedelta(days=1)

    with django_assert_num_queries(10):
        PaymentPlanService(top_up_pp).create_top_up_amendment(user, start, end)


@pytest.mark.parametrize(
    "plan_type",
    [
        PaymentPlan.PlanType.REGULAR,
        PaymentPlan.PlanType.FOLLOW_UP,
        PaymentPlan.PlanType.TOP_UP_AMENDMENT,
    ],
)
def test_create_top_up_amendment_arrange_non_top_up_origin_act_create_assert_raises(
    user: User, business_area: Any, cycle: ProgramCycle, plan_type: str
) -> None:
    source_pp = PaymentPlanFactory(business_area=business_area, program_cycle=cycle, plan_type=plan_type)
    start = source_pp.dispersion_start_date + timedelta(days=1)
    end = source_pp.dispersion_end_date + timedelta(days=1)

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(source_pp).create_top_up_amendment(user, start, end)

    assert "Top Up plan" in str(error.value.detail[0])


def test_create_top_up_amendment_arrange_no_eligible_payments_act_create_assert_raises(
    user: User, top_up_pp: PaymentPlan
) -> None:
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_PENDING)
    start = top_up_pp.dispersion_start_date + timedelta(days=1)
    end = top_up_pp.dispersion_end_date + timedelta(days=1)

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(top_up_pp).create_top_up_amendment(user, start, end)

    assert "no eligible payments" in str(error.value.detail[0]).lower()
