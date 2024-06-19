import pytest

from page_object.payment_verification.payment_verification import PaymentVerification

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.usefixtures("login")
class TestSmokePaymentVerification:
    def test_smoke_payment_verification(self, pagePaymentVerification: PaymentVerification) -> None:
        pagePaymentVerification.getNavPaymentVerification().click()
        pagePaymentVerification.screenshot("payment_verification")