from datetime import timedelta

from django.utils import timezone
import pytest

from extras.test_utils.factories import PaymentFactory, PaymentPlanFactory
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
