"""Guards for the child-plan async copy task (``prepare_child_payment_list_async_task_action``).

Two review findings are pinned here:

* **Idempotency** — the job is retried (``AsyncRetryJob``, ``acks_late``), so re-running the
  action for a plan whose payments were already copied must be a no-op, not an
  ``IntegrityError`` on the ``payment_plan_and_household`` unique constraint.
* **Empty copy is surfaced** — when the eligible set is consumed by a sibling child plan
  between request-time validation and the async copy, the child plan ends up with zero
  payments; it must be marked ``build_status=FAILED`` instead of left silently ``OPEN``.
"""

from types import SimpleNamespace
from typing import Any
from unittest import mock

from freezegun import freeze_time
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentFactory,
    PaymentListFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.payment.celery_tasks import prepare_child_payment_list_async_task_action
from hope.apps.payment.services.payment_list_services import PaymentListService
from hope.models import Payment, PaymentList, PaymentPlan, ProgramCycle, User

pytestmark = pytest.mark.django_db


def _run_copy_action(plan: PaymentList) -> bool:
    """Invoke the async action exactly as the worker would, with the job's config."""
    job: Any = SimpleNamespace(config={"payment_list_id": str(plan.id)})
    return prepare_child_payment_list_async_task_action(job)


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
        status=PaymentList.Status.ACCEPTED,
        name="Test Payment Plan",
    )


@pytest.fixture
def source_payment(regular_pp: PaymentList) -> Payment:
    return PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)


@pytest.fixture
def top_up_group(cycle: ProgramCycle, regular_pp: PaymentList) -> PaymentPlan:
    return PaymentPlanFactory(
        cycle=cycle, plan_type=PaymentList.PlanType.TOP_UP, source_payment_plan=regular_pp.payment_plan
    )


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=2.0)
def test_action_arrange_copied_top_up_act_run_again_assert_idempotent(
    get_exchange_rate_mock: Any,
    user: User,
    regular_pp: PaymentList,
    source_payment: Payment,
    top_up_group: Any,
) -> None:
    top_up_pp = PaymentListService(regular_pp).create_top_up(user, payment_plan=top_up_group)
    _run_copy_action(top_up_pp)
    count_after_first_run = top_up_pp.payment_items.count()

    _run_copy_action(top_up_pp)

    assert count_after_first_run == 1
    assert top_up_pp.payment_items.count() == count_after_first_run


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=2.0)
def test_action_arrange_eligible_payments_act_run_assert_build_status_ok(
    get_exchange_rate_mock: Any,
    user: User,
    regular_pp: PaymentList,
    source_payment: Payment,
    top_up_group: Any,
) -> None:
    top_up_pp = PaymentListService(regular_pp).create_top_up(user, payment_plan=top_up_group)

    _run_copy_action(top_up_pp)

    top_up_pp.refresh_from_db()
    assert top_up_pp.payment_items.count() == 1
    assert top_up_pp.build_status == PaymentList.BuildStatus.BUILD_STATUS_OK


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=2.0)
def test_action_arrange_plan_without_source_act_run_assert_skips_source_lock(
    get_exchange_rate_mock: Any,
    regular_pp: PaymentList,
) -> None:
    with mock.patch("hope.apps.payment.services.payment_list_services.PaymentListService") as service_cls:
        result = _run_copy_action(regular_pp)

    assert result is True
    service_cls.assert_called_once_with(payment_list=regular_pp)
    service_cls.return_value.create_child_plan_payments.assert_called_once_with(amounts=None, fixed_amount=None)


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=2.0)
def test_action_arrange_plan_deleted_act_run_assert_copy_skipped(
    get_exchange_rate_mock: Any,
    user: User,
    regular_pp: PaymentList,
    source_payment: Payment,
    top_up_group: Any,
) -> None:
    top_up_pp = PaymentListService(regular_pp).create_top_up(user, payment_plan=top_up_group)
    PaymentListService(payment_list=top_up_pp).delete()

    result = _run_copy_action(top_up_pp)

    assert result is True
    assert top_up_pp.payment_items.count() == 0


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=2.0)
def test_action_arrange_eligible_consumed_by_sibling_act_run_assert_build_status_failed(
    get_exchange_rate_mock: Any,
    user: User,
    regular_pp: PaymentList,
    source_payment: Payment,
    top_up_group: Any,
) -> None:
    first_top_up = PaymentListService(regular_pp).create_top_up(user, payment_plan=top_up_group)
    second_top_up = PaymentListService(regular_pp).create_top_up(user, payment_plan=top_up_group)
    _run_copy_action(first_top_up)

    _run_copy_action(second_top_up)

    second_top_up.refresh_from_db()
    assert second_top_up.payment_items.count() == 0
    assert second_top_up.build_status == PaymentList.BuildStatus.BUILD_STATUS_FAILED
