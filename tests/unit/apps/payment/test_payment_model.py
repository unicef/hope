from decimal import Decimal

import pytest

from extras.test_utils.factories.payment import FinancialServiceProviderFactory, PaymentFactory, PaymentPlanFactory
from hope.models import Payment

pytestmark = pytest.mark.django_db


@pytest.fixture
def payment_plan():
    return PaymentPlanFactory()


@pytest.fixture
def fsp_xlsx():
    return FinancialServiceProviderFactory(
        name="Test FSP XLSX",
        vision_vendor_number="123456",
        communication_channel="XLSX",
    )


@pytest.fixture
def payment_with_null_entitlement(payment_plan, fsp_xlsx):
    return PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=None,
        entitlement_quantity_usd=None,
        delivered_quantity=None,
        delivered_quantity_usd=None,
        status=Payment.STATUS_FORCE_FAILED,
        financial_service_provider=fsp_xlsx,
    )


def test_get_revert_mark_as_failed_status_raises_when_entitlement_quantity_is_none(payment_with_null_entitlement):
    with pytest.raises(ValueError, match="entitlement_quantity must not be None"):
        payment_with_null_entitlement.get_revert_mark_as_failed_status(Decimal("100.00"))
