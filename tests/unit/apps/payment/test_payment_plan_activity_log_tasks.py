from datetime import date, timedelta
from decimal import Decimal
from unittest import mock

import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.household import HouseholdFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.activity_log.utils import copy_model_object
from hope.apps.core.celery_tasks import async_retry_job_task
from hope.apps.payment.celery_tasks import (
    log_payment_plan_change,
    payment_plan_exclude_beneficiaries_async_task,
    update_exchange_rate_on_release_payments_async_task,
)
from hope.models import AsyncRetryJob, DataCollectingType, LogEntry, PaymentPlan, User

pytestmark = pytest.mark.django_db


def queue_and_run_retry_task(task: object, *args: object, **kwargs: object) -> object:
    with mock.patch("hope.apps.payment.celery_tasks.AsyncRetryJob.queue", autospec=True):
        task(*args, **kwargs)
    job = AsyncRetryJob.objects.latest("pk")
    return async_retry_job_task.run(job._meta.label_lower, job.pk, job.version)


@pytest.fixture
def user() -> User:
    return UserFactory(first_name="Log", last_name="Author")


@pytest.fixture
def program():
    return ProgramFactory(
        data_collecting_type=DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD),
        cycle=False,
    )


@pytest.fixture
def program_cycle(program):
    return ProgramCycleFactory(
        program=program,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
    )


@pytest.fixture
def payment_plan(program_cycle):
    return PaymentPlanFactory(status=PaymentPlan.Status.LOCKED, program_cycle=program_cycle)


@pytest.fixture
def households(program):
    return [HouseholdFactory(program=program), HouseholdFactory(program=program)]


@pytest.fixture
def payments(payment_plan, households):
    return [
        PaymentFactory(parent=payment_plan, household=households[0], collector=households[0].head_of_household),
        PaymentFactory(parent=payment_plan, household=households[1], collector=households[1].head_of_household),
    ]


@pytest.mark.enable_activity_log
def test_exclude_beneficiaries_task_creates_activity_log(payment_plan, households, payments, user) -> None:
    payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
    payment_plan.save(update_fields=["background_action_status"])

    queue_and_run_retry_task(
        payment_plan_exclude_beneficiaries_async_task,
        payment_plan=payment_plan,
        excluding_hh_or_ind_ids=[households[0].unicef_id],
        exclusion_reason="Excluded by audit test",
        user_id=str(user.pk),
    )

    logs = LogEntry.objects.filter(object_id=payment_plan.pk, action=LogEntry.UPDATE)
    assert logs.count() == 1
    log = logs.first()
    assert log.user == user
    assert log.business_area == payment_plan.business_area
    assert log.changes["exclusion_reason"]["to"] == "Excluded by audit test"


@pytest.mark.enable_activity_log
def test_log_payment_plan_change_captures_business_fields(payment_plan, user) -> None:
    old_payment_plan = copy_model_object(payment_plan)
    payment_plan.status = PaymentPlan.Status.TP_STEFICON_COMPLETED
    payment_plan.exchange_rate = Decimal("1.2345")
    payment_plan.total_delivered_quantity = Decimal("500.00")
    payment_plan.save(update_fields=["status", "exchange_rate", "total_delivered_quantity"])

    log_payment_plan_change(payment_plan, old_payment_plan, str(user.pk))

    log = LogEntry.objects.filter(object_id=payment_plan.pk).latest("timestamp")
    assert log.action == LogEntry.UPDATE
    assert log.user == user
    assert log.changes["status"]["to"] == PaymentPlan.Status.TP_STEFICON_COMPLETED
    # create_diff() normalizes Decimals before stringifying
    assert log.changes["exchange_rate"]["to"] == str(Decimal("1.2345").normalize())
    assert log.changes["total_delivered_quantity"]["to"] == str(Decimal("500.00").normalize())


@pytest.mark.enable_activity_log
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_update_exchange_rate_task_creates_activity_log(get_exchange_rate_mock, payment_plan, user) -> None:
    queue_and_run_retry_task(
        update_exchange_rate_on_release_payments_async_task,
        payment_plan=payment_plan,
        user_id=str(user.pk),
    )

    log = LogEntry.objects.filter(object_id=payment_plan.pk, action=LogEntry.UPDATE).latest("timestamp")
    assert log.user == user
    assert log.changes["exchange_rate"]["to"] == "2.0"


@pytest.mark.enable_activity_log
def test_log_payment_plan_change_with_no_user_is_system_action(payment_plan) -> None:
    old_payment_plan = copy_model_object(payment_plan)
    payment_plan.status = PaymentPlan.Status.FINISHED
    payment_plan.save(update_fields=["status"])

    log_payment_plan_change(payment_plan, old_payment_plan, None)

    log = LogEntry.objects.filter(object_id=payment_plan.pk).latest("timestamp")
    assert log.user is None
    assert log.changes["status"]["to"] == PaymentPlan.Status.FINISHED
