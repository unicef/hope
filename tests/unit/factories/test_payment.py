import pytest

from extras.test_utils.factories import (
    AccountFactory,
    AccountTypeFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)

pytestmark = pytest.mark.django_db


def test_payment_factories():
    assert PaymentPlanFactory()
    assert AccountTypeFactory()
    assert AccountFactory()
    assert PaymentFactory()
    assert PaymentVerificationSummaryFactory()
    assert PaymentVerificationPlanFactory()
    assert PaymentVerificationFactory()
    assert DeliveryMechanismFactory()
    assert FinancialServiceProviderFactory()
    assert FinancialServiceProviderXlsxTemplateFactory()
