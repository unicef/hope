from typing import Any

from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.test import RequestFactory
import pytest

from extras.test_utils.factories import PaymentPlanFactory, UserFactory
from hope.admin.payment_plan import PaymentPlanAdmin
from hope.models import LogEntry, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def payment_plan() -> PaymentPlan:
    return PaymentPlanFactory()


@pytest.fixture
def admin_instance() -> PaymentPlanAdmin:
    return PaymentPlanAdmin(PaymentPlan, AdminSite())


@pytest.fixture
def admin_request() -> HttpRequest:
    request = RequestFactory().post("/")
    request.user = UserFactory()
    return request


@pytest.mark.enable_activity_log
@pytest.mark.parametrize(
    ("field", "new_value", "old_value"),
    [
        ("use_payment_gateway", True, False),
        ("status", PaymentPlan.Status.LOCKED, PaymentPlan.Status.OPEN),
    ],
)
def test_payment_plan_admin_save_logs_edit(
    payment_plan: PaymentPlan,
    admin_instance: PaymentPlanAdmin,
    admin_request: HttpRequest,
    django_assert_num_queries: Any,
    field: str,
    new_value: Any,
    old_value: Any,
) -> None:
    setattr(payment_plan, field, new_value)

    admin_instance.save_model(admin_request, payment_plan, form=None, change=True)

    with django_assert_num_queries(1):
        log = LogEntry.objects.get(object_id=payment_plan.pk, action=LogEntry.UPDATE)
    assert log.changes[field] == {"from": old_value, "to": new_value}
    assert log.user == admin_request.user
    assert list(log.programs.values_list("pk", flat=True)) == [payment_plan.cycle.program.pk]


@pytest.mark.enable_activity_log
def test_payment_plan_admin_save_without_mapped_change_does_not_log(
    payment_plan: PaymentPlan,
    admin_instance: PaymentPlanAdmin,
    admin_request: HttpRequest,
    django_assert_num_queries: Any,
) -> None:
    admin_instance.save_model(admin_request, payment_plan, form=None, change=True)

    with django_assert_num_queries(1):
        assert not LogEntry.objects.filter(object_id=payment_plan.pk).exists()
