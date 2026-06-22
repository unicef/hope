"""Regression guard for the extraction of the shared child-plan core.

``create_follow_up`` / ``create_follow_up_payments`` were refactored to share
``_create_child_payment_plan`` / ``_copy_payments`` with the top-up flows. Unlike
top-up, follow-up must still COPY the source entitlement and keep ``is_follow_up``.
"""

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
def regular_pp(business_area: Any, cycle: ProgramCycle) -> PaymentPlan:
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        name="Test Payment Plan",
    )


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_follow_up_arrange_failed_payment_act_run_task_assert_entitlement_copied(
    get_exchange_rate_mock: Any,
    user: User,
    regular_pp: PaymentPlan,
    django_capture_on_commit_callbacks: Any,
) -> None:
    failed_payment = PaymentFactory(parent=regular_pp, status=Payment.STATUS_ERROR)
    failed_payment.entitlement_quantity = Decimal("250.00")
    failed_payment.entitlement_quantity_usd = Decimal("125.00")
    failed_payment.save()
    start = regular_pp.dispersion_start_date + timedelta(days=1)
    end = regular_pp.dispersion_end_date + timedelta(days=1)

    follow_up_pp = PaymentPlanService(regular_pp).create_follow_up(user, start, end)
    with django_capture_on_commit_callbacks(execute=True):
        prepare_child_payment_plan_async_task(follow_up_pp)

    follow_up_pp.refresh_from_db()
    assert follow_up_pp.plan_type == PaymentPlan.PlanType.FOLLOW_UP
    assert follow_up_pp.name == "Test Payment Plan Follow Up"
    copied = follow_up_pp.payment_items.get()
    assert copied.source_payment == failed_payment
    assert copied.is_follow_up is True
    assert copied.entitlement_quantity == Decimal("250.00")
    assert copied.entitlement_quantity_usd == Decimal("125.00")


def test_create_follow_up_arrange_follow_up_origin_act_create_assert_raises(
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
        PaymentPlanService(follow_up_pp).create_follow_up(user, start, end)

    assert "follow-up of a follow-up" in str(error.value.detail[0])


def test_create_follow_up_arrange_no_unsuccessful_payments_act_create_assert_raises(
    user: User, regular_pp: PaymentPlan
) -> None:
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    start = regular_pp.dispersion_start_date + timedelta(days=1)
    end = regular_pp.dispersion_end_date + timedelta(days=1)

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(regular_pp).create_follow_up(user, start, end)

    assert "no unsuccessful payments" in str(error.value.detail[0])
