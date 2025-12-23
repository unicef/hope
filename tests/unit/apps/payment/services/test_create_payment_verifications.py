from django.test import TestCase

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from hope.apps.payment.services.create_payment_verifications import CreatePaymentVerifications
from hope.models import PaymentVerification


class TestCreatePaymentVerifications(TestCase):
    def setUp(self) -> None:
        create_afghanistan()

    def test_creates_payment_verifications_in_batches(self) -> None:
        payment_plan = PaymentPlanFactory()
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)
        PaymentFactory.create_batch(
            5,
            parent=payment_plan,
            business_area=payment_plan.business_area,
        )

        service = CreatePaymentVerifications(verification_plan, payment_plan.payment_items.all())
        service.BATCH_SIZE = 2
        service.create()

        created = PaymentVerification.objects.filter(payment_verification_plan=verification_plan)
        assert created.count() == 5
        assert all(pv.received_amount is None for pv in created)
