import pytest

from extras.test_utils.factories import (
    PaymentFactory,
    PaymentVerificationPlanFactory,
)
from hope.apps.payment.services.create_payment_verifications import CreatePaymentVerifications
from hope.models import Payment, PaymentVerification, PaymentVerificationPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def verification_plan() -> PaymentVerificationPlan:
    return PaymentVerificationPlanFactory()


@pytest.fixture
def payments(verification_plan: PaymentVerificationPlan) -> list[Payment]:
    return PaymentFactory.create_batch(
        5,
        parent=verification_plan.payment_plan,
        business_area=verification_plan.payment_plan.business_area,
    )


def test_creates_payment_verifications_in_batches(
    verification_plan: PaymentVerificationPlan, payments: list[Payment]
) -> None:
    payment_plan = verification_plan.payment_plan
    service = CreatePaymentVerifications(verification_plan, payment_plan.payment_items.all())
    service.BATCH_SIZE = 2
    service.create()

    created = PaymentVerification.objects.filter(payment_verification_plan=verification_plan)
    assert created.count() == 5
    assert all(pv.received_amount is None for pv in created)


def test_create_skips_when_no_payments(verification_plan: PaymentVerificationPlan) -> None:
    payment_plan = verification_plan.payment_plan
    service = CreatePaymentVerifications(verification_plan, payment_plan.payment_items.none())
    service.create()

    assert PaymentVerification.objects.filter(payment_verification_plan=verification_plan).count() == 0
