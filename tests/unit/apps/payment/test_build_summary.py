import pytest

from extras.test_utils.factories import (
    PaymentListFactory,
    PaymentVerificationPlanFactory,
)
from hope.models import PaymentList, PaymentVerificationPlan, PaymentVerificationSummary, build_summary

pytestmark = pytest.mark.django_db


@pytest.fixture
def payment_list():
    return PaymentListFactory(
        status=PaymentList.Status.FINISHED,
    )


@pytest.fixture
def payment_verification_plan_active(payment_list):
    return PaymentVerificationPlanFactory(
        payment_list=payment_list,
        status=PaymentVerificationPlan.STATUS_ACTIVE,
    )


@pytest.fixture
def payment_verification_plan_finished(payment_list):
    return PaymentVerificationPlanFactory(
        payment_list=payment_list,
        status=PaymentVerificationPlan.STATUS_FINISHED,
    )


@pytest.fixture
def payment_verification_plan_pending(payment_list):
    return PaymentVerificationPlanFactory(
        payment_list=payment_list,
        status=PaymentVerificationPlan.STATUS_PENDING,
    )


def test_status_pending_when_zero_verifications(payment_list) -> None:
    build_summary(payment_list)

    summary = payment_list.payment_verification_summary

    assert summary.status == PaymentVerificationSummary.STATUS_PENDING


def test_status_active_when_at_least_one_active_verification(payment_list, payment_verification_plan_active) -> None:
    build_summary(payment_list)

    summary = payment_list.payment_verification_summary
    assert summary.status == PaymentVerificationSummary.STATUS_ACTIVE


def test_status_finished_when_all_verifications_finished(payment_list, payment_verification_plan_finished) -> None:
    build_summary(payment_list)

    summary = payment_list.payment_verification_summary
    assert summary.status == PaymentVerificationSummary.STATUS_FINISHED


def test_status_pending_when_add_and_removed_verification(payment_list, payment_verification_plan_pending) -> None:
    payment_verification_plan_pending.delete()

    build_summary(payment_list)

    summary = payment_list.payment_verification_summary
    assert summary.status == PaymentVerificationSummary.STATUS_PENDING


def test_query_number(payment_list, django_assert_num_queries) -> None:
    with django_assert_num_queries(3):
        build_summary(payment_list)
