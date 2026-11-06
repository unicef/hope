import pytest

from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentListFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from hope.models import PaymentList, PaymentVerification, PaymentVerificationPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def payment_list():
    return PaymentListFactory(status=PaymentList.Status.FINISHED)


@pytest.fixture
def payment_verification_plan(payment_list):
    return PaymentVerificationPlanFactory(
        payment_list=payment_list,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
    )


@pytest.fixture
def payment(payment_list):
    return PaymentFactory(parent=payment_list)


@pytest.fixture
def payment_verification_with_null_status_date(payment_verification_plan, payment):
    verification = PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan,
        payment=payment,
        status=PaymentVerification.STATUS_PENDING,
    )
    verification.status_date = None
    verification.save(update_fields=["status_date"])
    return verification


def test_is_manually_editable_raises_when_status_date_is_none(payment_verification_with_null_status_date):
    with pytest.raises(ValueError, match="status_date must not be None"):
        _ = payment_verification_with_null_status_date.is_manually_editable


def test_is_manually_editable_returns_false_when_not_manual_channel(payment_list, payment):
    plan = PaymentVerificationPlanFactory(
        payment_list=payment_list,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
    )
    verification = PaymentVerificationFactory(
        payment_verification_plan=plan,
        payment=payment,
        status=PaymentVerification.STATUS_PENDING,
    )

    assert verification.is_manually_editable is False
