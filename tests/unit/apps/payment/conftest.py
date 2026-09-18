import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import (
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)


@pytest.fixture
def payment_ba():
    return BusinessAreaFactory(slug="payment-test")


@pytest.fixture
def payment_verification_pr_42(payment_ba):
    pvp = PaymentVerificationPlanFactory(payment_plan__business_area=payment_ba)
    pv = PaymentVerificationFactory(
        payment_verification_plan=pvp,
        payment__parent=pvp.payment_plan,
    )
    pv.payment.unicef_id = "PR-0000042"
    pv.payment.save(update_fields=["unicef_id"])
    return pv


@pytest.fixture
def payment_verification_pr_99(payment_ba):
    pvp = PaymentVerificationPlanFactory(payment_plan__business_area=payment_ba)
    pv = PaymentVerificationFactory(
        payment_verification_plan=pvp,
        payment__parent=pvp.payment_plan,
    )
    pv.payment.unicef_id = "PR-0000099"
    pv.payment.save(update_fields=["unicef_id"])
    return pv


@pytest.fixture
def payment_plan_with_cycle(payment_ba):
    pp = PaymentPlanFactory(
        name="Emergency Relief Plan",
        program_cycle__title="Quarterly Cash Q3",
        business_area=payment_ba,
    )
    pp.unicef_id = "PP-0000001"
    pp.save(update_fields=["unicef_id"])
    return pp


@pytest.fixture
def payment_plan_other(payment_ba):
    pp = PaymentPlanFactory(
        name="Standard Distribution",
        program_cycle__title="Voucher Program",
        business_area=payment_ba,
    )
    pp.unicef_id = "PP-0000002"
    pp.save(update_fields=["unicef_id"])
    return pp
