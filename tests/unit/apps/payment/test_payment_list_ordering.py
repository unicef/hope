from datetime import timedelta

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hope.apps.payment.api.filters import PaymentSearchFilter
from hope.models import Payment

pytestmark = pytest.mark.django_db


@pytest.fixture
def payments_with_distinct_created_at() -> tuple[Payment, Payment, Payment]:
    plan = PaymentPlanFactory()
    now = timezone.now()
    oldest = PaymentFactory(parent=plan)
    middle = PaymentFactory(parent=plan)
    newest = PaymentFactory(parent=plan)
    Payment.objects.filter(pk=oldest.pk).update(created_at=now - timedelta(days=2))
    Payment.objects.filter(pk=middle.pk).update(created_at=now - timedelta(days=1))
    Payment.objects.filter(pk=newest.pk).update(created_at=now)
    return oldest, middle, newest


def test_payment_search_filter_orders_by_created_at_ascending(
    payments_with_distinct_created_at: tuple[Payment, Payment, Payment],
) -> None:
    oldest, middle, newest = payments_with_distinct_created_at

    result = PaymentSearchFilter(data={"ordering": "created_at"}, queryset=Payment.objects.all()).qs

    assert list(result.values_list("pk", flat=True)) == [oldest.pk, middle.pk, newest.pk]


def test_payment_search_filter_orders_by_created_at_descending(
    payments_with_distinct_created_at: tuple[Payment, Payment, Payment],
) -> None:
    oldest, middle, newest = payments_with_distinct_created_at

    result = PaymentSearchFilter(data={"ordering": "-created_at"}, queryset=Payment.objects.all()).qs

    assert list(result.values_list("pk", flat=True)) == [newest.pk, middle.pk, oldest.pk]


def test_payment_search_filter_orders_by_admin2_name() -> None:
    plan = PaymentPlanFactory()
    payment_b = PaymentFactory(parent=plan, household__admin2=AreaFactory(name="B District"))
    payment_a = PaymentFactory(parent=plan, household__admin2=AreaFactory(name="A District"))

    result = PaymentSearchFilter(data={"ordering": "household__admin2__name"}, queryset=Payment.objects.all()).qs

    assert list(result.values_list("pk", flat=True)) == [payment_a.pk, payment_b.pk]


def test_payment_search_filter_orders_by_fsp_name() -> None:
    plan = PaymentPlanFactory()
    payment_b = PaymentFactory(parent=plan, financial_service_provider=FinancialServiceProviderFactory(name="B FSP"))
    payment_a = PaymentFactory(parent=plan, financial_service_provider=FinancialServiceProviderFactory(name="A FSP"))

    result = PaymentSearchFilter(
        data={"ordering": "financial_service_provider__name"}, queryset=Payment.objects.all()
    ).qs

    assert list(result.values_list("pk", flat=True)) == [payment_a.pk, payment_b.pk]


def test_payment_search_filter_orders_by_entitlement_quantity_usd() -> None:
    plan = PaymentPlanFactory()
    high = PaymentFactory(parent=plan, entitlement_quantity_usd=100)
    low = PaymentFactory(parent=plan, entitlement_quantity_usd=10)

    result = PaymentSearchFilter(data={"ordering": "entitlement_quantity_usd"}, queryset=Payment.objects.all()).qs

    assert list(result.values_list("pk", flat=True)) == [low.pk, high.pk]


def test_payment_search_filter_orders_by_delivered_quantity() -> None:
    plan = PaymentPlanFactory()
    high = PaymentFactory(parent=plan, delivered_quantity=100)
    low = PaymentFactory(parent=plan, delivered_quantity=10)

    result = PaymentSearchFilter(data={"ordering": "delivered_quantity"}, queryset=Payment.objects.all()).qs

    assert list(result.values_list("pk", flat=True)) == [low.pk, high.pk]


def test_payment_search_filter_orders_by_fsp_auth_code() -> None:
    plan = PaymentPlanFactory()
    payment_b = PaymentFactory(parent=plan, fsp_auth_code="B-CODE")
    payment_a = PaymentFactory(parent=plan, fsp_auth_code="A-CODE")

    result = PaymentSearchFilter(data={"ordering": "fsp_auth_code"}, queryset=Payment.objects.all()).qs

    assert list(result.values_list("pk", flat=True)) == [payment_a.pk, payment_b.pk]


def test_payment_search_filter_orders_by_mark() -> None:
    plan = PaymentPlanFactory()
    success = PaymentFactory(parent=plan, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    partial = PaymentFactory(parent=plan, status=Payment.STATUS_DISTRIBUTION_PARTIAL)
    not_distributed = PaymentFactory(parent=plan, status=Payment.STATUS_NOT_DISTRIBUTED)
    pending = PaymentFactory(parent=plan, status=Payment.STATUS_PENDING)

    result = PaymentSearchFilter(data={"ordering": "mark"}, queryset=Payment.objects.all()).qs

    assert list(result.values_list("pk", flat=True)) == [
        success.pk,
        partial.pk,
        not_distributed.pk,
        pending.pk,
    ]
