from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils import timezone
import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.household import HouseholdFactory
from extras.test_utils.factories.payment import FinancialServiceProviderFactory, PaymentFactory, PaymentPlanFactory
from hope.models import Payment

pytestmark = pytest.mark.django_db


@pytest.fixture
def payment_plan():
    return PaymentPlanFactory()


@pytest.fixture
def fsp_api():
    return FinancialServiceProviderFactory(
        name="Test FSP API",
        vision_vendor_number="1232345",
        communication_channel="API",
    )


@pytest.fixture
def fsp_xlsx():
    return FinancialServiceProviderFactory(
        name="Test FSP",
        vision_vendor_number="123465",
        communication_channel="XLSX",
    )


@pytest.fixture
def fsp_sftp():
    return FinancialServiceProviderFactory(
        name="Test FSP-SFTP",
        vision_vendor_number="012344",
        communication_channel="SFTP",
    )


def test_payment_unique_together():
    payment_plan = PaymentPlanFactory()
    household = HouseholdFactory()
    PaymentFactory(parent=payment_plan, household=household)
    with transaction.atomic():
        with pytest.raises(IntegrityError):
            PaymentFactory(parent=payment_plan, household=household)


def test_household_admin2_property(payment_plan):
    admin2 = AreaFactory(name="New admin2")
    household = HouseholdFactory(admin2=admin2)
    payment = PaymentFactory(parent=payment_plan, household=household)
    assert payment.household_admin2 == admin2.name


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (Payment.STATUS_PENDING, "Pending"),
        (Payment.STATUS_DISTRIBUTION_SUCCESS, "Delivered Fully"),
        (Payment.STATUS_SUCCESS, "Delivered Fully"),
        (Payment.STATUS_DISTRIBUTION_PARTIAL, "Delivered Partially"),
        (Payment.STATUS_NOT_DISTRIBUTED, "Not Delivered"),
        (Payment.STATUS_ERROR, "Unsuccessful"),
        (Payment.STATUS_FORCE_FAILED, "Force Failed"),
        (Payment.STATUS_MANUALLY_CANCELLED, "-"),
    ],
)
def test_payment_status_property(payment_plan, status, expected):
    payment = PaymentFactory(parent=payment_plan, status=status)
    assert payment.payment_status == expected


def test_mark_as_failed(payment_plan, fsp_xlsx):
    payment_invalid_status = PaymentFactory(
        parent=payment_plan, status=Payment.STATUS_FORCE_FAILED, financial_service_provider=fsp_xlsx
    )
    payment = PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("999.00"),
        delivered_quantity=Decimal("111.00"),
        delivered_quantity_usd=Decimal("22.00"),
        status=Payment.STATUS_DISTRIBUTION_PARTIAL,
        financial_service_provider=fsp_xlsx,
    )
    with pytest.raises(ValidationError, match="Status shouldn't be failed"):
        payment_invalid_status.mark_as_failed()

    payment.mark_as_failed()
    payment.save()
    payment.refresh_from_db()
    assert payment.delivered_quantity == 0
    assert payment.delivered_quantity_usd == 0
    assert payment.delivery_date is None
    assert payment.status == Payment.STATUS_FORCE_FAILED


def test_revert_mark_as_failed(payment_plan, fsp_xlsx):
    payment_entitlement_quantity_none = PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=None,
        entitlement_quantity_usd=None,
        delivered_quantity=None,
        delivered_quantity_usd=None,
        status=Payment.STATUS_FORCE_FAILED,
        financial_service_provider=fsp_xlsx,
    )
    payment_invalid_status = PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("999.00"),
        status=Payment.STATUS_PENDING,
        financial_service_provider=fsp_xlsx,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("999.00"),
        delivered_quantity=Decimal("111.00"),
        status=Payment.STATUS_FORCE_FAILED,
        financial_service_provider=fsp_xlsx,
    )
    date = timezone.now().date()

    with pytest.raises(ValidationError, match="Only payment marked as force failed can be reverted"):
        payment_invalid_status.revert_mark_as_failed(Decimal("999.00"), date)

    with pytest.raises(ValidationError, match="Entitlement quantity need to be set in order to revert"):
        payment_entitlement_quantity_none.revert_mark_as_failed(Decimal("999.00"), date)

    payment.revert_mark_as_failed(Decimal("999.00"), date)
    payment.save()
    payment.refresh_from_db()
    assert payment.delivered_quantity == 999
    assert payment.delivery_date.date() == date
    assert payment.status == Payment.STATUS_DISTRIBUTION_SUCCESS


def test_get_revert_mark_as_failed_status(payment_plan, fsp_xlsx):
    payment = PaymentFactory(
        parent=payment_plan, entitlement_quantity=Decimal("999.00"), financial_service_provider=fsp_xlsx
    )
    delivered_quantity_with_status = (
        (0, Payment.STATUS_NOT_DISTRIBUTED),
        (100, Payment.STATUS_DISTRIBUTION_PARTIAL),
        (999, Payment.STATUS_DISTRIBUTION_SUCCESS),
    )
    for delivered_quantity, status in delivered_quantity_with_status:
        result_status = payment.get_revert_mark_as_failed_status(delivered_quantity)
        assert result_status == status

    with pytest.raises(ValidationError, match="Wrong delivered quantity 1000 for entitlement quantity 999"):
        payment.get_revert_mark_as_failed_status(1000)


def test_validate_payment_fsp_communication_channel(payment_plan, fsp_api, fsp_sftp):
    payment_api = PaymentFactory(
        parent=payment_plan, entitlement_quantity=Decimal("1.00"), financial_service_provider=fsp_api
    )
    payment_sftp = PaymentFactory(
        parent=payment_plan, entitlement_quantity=Decimal("1.00"), financial_service_provider=fsp_sftp
    )

    with pytest.raises(
        DRFValidationError, match="Only Payment with FSP communication channel XLSX can be manually mark as failed"
    ):
        payment_api.validate_payment_fsp_communication_channel()

    with pytest.raises(
        DRFValidationError, match="Only Payment with FSP communication channel XLSX can be manually mark as failed"
    ):
        payment_sftp.validate_payment_fsp_communication_channel()
