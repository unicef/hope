from typing import Any

from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.test import Client, RequestFactory
from django.urls import reverse
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


@pytest.fixture
def locked_payment_gateway_plan() -> PaymentPlan:
    return PaymentPlanFactory(name="Locked gateway plan", status=PaymentPlan.Status.LOCKED, use_payment_gateway=True)


def test_payment_plan_changelist_shows_the_plan_workflow_columns(
    admin_client: Client, locked_payment_gateway_plan: PaymentPlan
) -> None:
    response = admin_client.get(reverse("admin:payment_paymentplan_changelist"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "column-status" in content
    assert "column-background_action_status" in content
    assert "column-plan_type" in content
    assert "column-use_payment_gateway" in content
    assert "Locked gateway plan" in content


def test_payment_plan_change_form_keeps_workflow_fields_read_only(
    payment_plan: PaymentPlan, admin_instance: PaymentPlanAdmin, admin_request: HttpRequest
) -> None:
    form_class = admin_instance.get_form(admin_request, payment_plan)

    assert sorted(form_class.base_fields) == ["background_action_status", "use_payment_gateway"]


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
    assert log.changes[field] == {"from": str(old_value), "to": str(new_value)}
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
