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


@pytest.mark.parametrize(
    ("ordering", "first_kwargs", "second_kwargs"),
    [
        pytest.param(
            "household__admin2__name",
            lambda: {"household__admin2": AreaFactory(name="A District")},
            lambda: {"household__admin2": AreaFactory(name="B District")},
            id="admin2_name",
        ),
        pytest.param(
            "financial_service_provider__name",
            lambda: {"financial_service_provider": FinancialServiceProviderFactory(name="A FSP")},
            lambda: {"financial_service_provider": FinancialServiceProviderFactory(name="B FSP")},
            id="fsp_name",
        ),
        pytest.param(
            "entitlement_quantity_usd",
            lambda: {"entitlement_quantity_usd": 10},
            lambda: {"entitlement_quantity_usd": 100},
            id="entitlement_quantity_usd",
        ),
        pytest.param(
            "delivered_quantity",
            lambda: {"delivered_quantity": 10},
            lambda: {"delivered_quantity": 100},
            id="delivered_quantity",
        ),
        pytest.param(
            "fsp_auth_code",
            lambda: {"fsp_auth_code": "A-CODE"},
            lambda: {"fsp_auth_code": "B-CODE"},
            id="fsp_auth_code",
        ),
    ],
)
def test_payment_search_filter_orders_by_column(ordering: str, first_kwargs, second_kwargs) -> None:
    plan = PaymentPlanFactory()
    # Created in reverse so the assertion cannot pass on insertion order alone.
    second = PaymentFactory(parent=plan, **second_kwargs())
    first = PaymentFactory(parent=plan, **first_kwargs())

    result = PaymentSearchFilter(data={"ordering": ordering}, queryset=Payment.objects.all()).qs

    assert list(result.values_list("pk", flat=True)) == [first.pk, second.pk]


def test_payment_search_filter_orders_by_reconciliation_rank() -> None:
    """Statuses outside the reconciled/failed set must sort with their peers, not in a NULL clump."""
    plan = PaymentPlanFactory()
    sent_to_fsp = PaymentFactory(parent=plan, status=Payment.STATUS_SENT_TO_FSP)
    not_distributed = PaymentFactory(parent=plan, status=Payment.STATUS_NOT_DISTRIBUTED)
    transaction_successful = PaymentFactory(parent=plan, status=Payment.STATUS_SUCCESS)
    partially_distributed = PaymentFactory(parent=plan, status=Payment.STATUS_DISTRIBUTION_PARTIAL)

    result = PaymentSearchFilter(data={"ordering": "reconciliation_rank"}, queryset=Payment.objects.all()).qs

    assert list(result.values_list("pk", flat=True)) == [
        transaction_successful.pk,
        partially_distributed.pk,
        not_distributed.pk,
        sent_to_fsp.pk,
    ]


def test_payment_search_filter_ranks_every_payment_status() -> None:
    """No status may fall through the Case: NULL sorts arbitrarily, and 99 is the unranked sentinel."""
    plan = PaymentPlanFactory()
    for status, _label in Payment.STATUS_CHOICE:
        payment = PaymentFactory(parent=plan)
        Payment.objects.filter(pk=payment.pk).update(status=status)

    result = PaymentSearchFilter(data={"ordering": "reconciliation_rank"}, queryset=Payment.objects.all()).qs

    assert result.count() == len(Payment.STATUS_CHOICE)
    assert not result.filter(reconciliation_rank__isnull=True).exists()
    assert not result.filter(reconciliation_rank=99).exists()


def test_payment_search_filter_breaks_ties_deterministically() -> None:
    """Ties need a unique tie-breaker, otherwise LIMIT/OFFSET paging can repeat or skip a row."""
    plan = PaymentPlanFactory()
    payments = [PaymentFactory(parent=plan, status=Payment.STATUS_PENDING) for _ in range(5)]

    result = PaymentSearchFilter(data={"ordering": "reconciliation_rank"}, queryset=Payment.objects.all()).qs

    assert list(result.values_list("pk", flat=True)) == sorted(payment.pk for payment in payments)


def test_payment_search_filter_breaks_ties_deterministically_without_ordering() -> None:
    plan = PaymentPlanFactory()
    now = timezone.now()
    payments = [PaymentFactory(parent=plan) for _ in range(5)]
    Payment.objects.filter(pk__in=[payment.pk for payment in payments]).update(created_at=now)

    result = PaymentSearchFilter(data={}, queryset=Payment.objects.all()).qs

    assert list(result.values_list("pk", flat=True)) == sorted(payment.pk for payment in payments)


def test_payment_search_filter_rejects_collector_id_ordering() -> None:
    """The Collector column shows a snapshot name, so its UUID is not a meaningful sort key."""
    filterset = PaymentSearchFilter(data={"ordering": "collector_id"}, queryset=Payment.objects.all())

    assert not filterset.is_valid()
    assert "ordering" in filterset.errors
