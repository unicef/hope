import pytest

from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from hope.models import PaymentPlan, PaymentVerification, PaymentVerificationPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def payment_plan():
    return PaymentPlanFactory(status=PaymentPlan.Status.FINISHED)


@pytest.fixture
def payment_verification_plan(payment_plan):
    return PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
    )


@pytest.fixture
def payment(payment_plan):
    return PaymentFactory(parent=payment_plan)


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


def test_is_manually_editable_returns_false_when_not_manual_channel(payment_plan, payment):
    plan = PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
    )
    verification = PaymentVerificationFactory(
        payment_verification_plan=plan,
        payment=payment,
        status=PaymentVerification.STATUS_PENDING,
    )

    assert verification.is_manually_editable is False
