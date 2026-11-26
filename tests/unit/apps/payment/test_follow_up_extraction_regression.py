"""Regression guard for the extraction of the shared child-plan core.

``create_follow_up`` / ``create_follow_up_payments`` were refactored to share
``_create_child_payment_list`` / ``_copy_payments`` with the top-up flows. Unlike
top-up, follow-up must still COPY the source entitlement and keep ``is_follow_up``.
"""

from decimal import Decimal
from typing import Any
from unittest import mock

from freezegun import freeze_time
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentFactory,
    PaymentListFactory,
    PaymentPlanFactory,
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
    program = ProgramFactory(business_area=business_area)
    return ProgramCycleFactory(program=program)


@pytest.fixture
def regular_pp(business_area: Any, cycle: ProgramCycle) -> PaymentList:
    return PaymentListFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentList.PlanType.REGULAR,
        name="Test Payment Plan",
    )


@pytest.fixture
def follow_up_group(cycle: ProgramCycle, regular_pp: PaymentList) -> PaymentPlan:
    return PaymentPlanFactory(
        cycle=cycle, plan_type=PaymentList.PlanType.FOLLOW_UP, source_payment_plan=regular_pp.payment_plan
    )


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=2.0)
def test_create_follow_up_arrange_failed_payment_act_run_task_assert_entitlement_copied(
    get_exchange_rate_mock: Any,
    user: User,
    regular_pp: PaymentList,
    django_capture_on_commit_callbacks: Any,
    follow_up_group: Any,
) -> None:
    failed_payment = PaymentFactory(parent=regular_pp, status=Payment.STATUS_ERROR)
    failed_payment.entitlement_quantity = Decimal("250.00")
    failed_payment.entitlement_quantity_usd = Decimal("125.00")
    failed_payment.save()

    follow_up_pp = PaymentListService(regular_pp).create_follow_up(user, payment_plan=follow_up_group)
    with django_capture_on_commit_callbacks(execute=True):
        prepare_child_payment_list_async_task(follow_up_pp)

    follow_up_pp.refresh_from_db()
    assert follow_up_pp.plan_type == PaymentList.PlanType.FOLLOW_UP
    assert follow_up_pp.name == "Test Payment Plan Follow Up"
    copied = follow_up_pp.payment_items.get()
    assert copied.source_payment == failed_payment
    assert copied.is_follow_up is True
    assert copied.entitlement_quantity == Decimal("250.00")
    assert copied.entitlement_quantity_usd == Decimal("125.00")


def test_create_follow_up_arrange_follow_up_origin_act_create_assert_raises(
    user: User, business_area: Any, cycle: ProgramCycle, follow_up_group: Any
) -> None:
    follow_up_pp = PaymentListFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
    )

    with pytest.raises(ValidationError) as error:
        PaymentListService(follow_up_pp).create_follow_up(user, payment_plan=follow_up_group)

    assert "follow-up of a follow-up" in str(error.value.detail[0])


def test_create_follow_up_arrange_no_unsuccessful_payments_act_create_assert_raises(
    user: User, regular_pp: PaymentList, follow_up_group: Any
) -> None:
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    with pytest.raises(ValidationError) as error:
        PaymentListService(regular_pp).create_follow_up(user, payment_plan=follow_up_group)

    assert "no unsuccessful payments" in str(error.value.detail[0])
