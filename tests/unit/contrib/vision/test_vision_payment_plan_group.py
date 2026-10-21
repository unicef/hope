from decimal import Decimal

from django.db import transaction
import pytest

from extras.test_utils.factories import (
    ApprovalProcessFactory,
    CurrencyFactory,
    FinancialServiceProviderFactory,
    PaymentPlanFactory,
)
from hope.apps.payment.services.payment_plan_group_services import PaymentPlanGroupService
from hope.contrib.api.serializers.vision import PaymentPlanGroupPayloadSerializer
from hope.contrib.vision.choices import VisionStatus
from hope.contrib.vision.services import VisionService
from hope.contrib.vision.views import PaymentPlanCallbackView
from hope.models import Approval, PaymentPlan, PaymentPlanGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def group_with_plans() -> tuple[PaymentPlanGroup, PaymentPlan, PaymentPlan]:
    first = PaymentPlanFactory(
        total_entitled_quantity=Decimal("10.00"),
        total_entitled_quantity_usd=Decimal("8.00"),
        internal_data={"vision": {"status": VisionStatus.RELEASED.value}},
    )
    second = PaymentPlanFactory(
        program_cycle=first.program_cycle,
        payment_plan_group=first.payment_plan_group,
        total_entitled_quantity=Decimal("20.00"),
        total_entitled_quantity_usd=Decimal("16.00"),
    )
    group = first.payment_plan_group
    group.financial_service_provider = FinancialServiceProviderFactory()
    group.currency = CurrencyFactory()
    group.save(update_fields=["financial_service_provider", "currency"])
    return group, first, second


@pytest.fixture
def group_in_review(group_with_plans) -> tuple[PaymentPlanGroup, PaymentPlan, PaymentPlan]:
    group, first, second = group_with_plans
    group.status = PaymentPlanGroup.Status.IN_REVIEW
    group.save(update_fields=["status"])
    PaymentPlan.objects.filter(pk__in=[first.pk, second.pk]).update(status=PaymentPlan.Status.IN_REVIEW)
    ApprovalProcessFactory(payment_plan_group=group)
    return group, first, second


def test_group_vision_payload_sums_plan_amounts(group_with_plans, django_assert_num_queries) -> None:
    group, _, _ = group_with_plans
    with django_assert_num_queries(2):
        local_total = group.total_entitled_quantity
        usd_total = group.total_entitled_quantity_usd
    payload = PaymentPlanGroupPayloadSerializer(group).data

    assert local_total == Decimal("30.00")
    assert usd_total == Decimal("24.00")
    assert payload["payplanSno"] == group.unicef_id
    assert payload["authAmt"] == "30.00"
    assert payload["authAmtUsd"] == "24.00"
    assert payload["exchangeRate"] is None


def test_callback_lookup_resolves_group_unicef_id(group_with_plans, django_assert_num_queries) -> None:
    group, _, _ = group_with_plans
    with transaction.atomic(), django_assert_num_queries(1):
        selected = PaymentPlanCallbackView._get_payment_plan_group(group.unicef_id)

    assert selected.pk == group.pk


def test_group_vision_state_leaves_old_plan_data_untouched(group_with_plans, django_assert_num_queries) -> None:
    group, first, _ = group_with_plans
    with django_assert_num_queries(0):
        VisionService.set_status(group, VisionStatus.WAITING_FOR_CALLBACK)
        group_status = group.vision_status
        plan_data = first.internal_data["vision"].copy()

    assert group_status == VisionStatus.WAITING_FOR_CALLBACK.value
    assert plan_data == {"status": VisionStatus.RELEASED.value}


def test_vision_release_accepts_group_once(group_in_review, monkeypatch) -> None:
    group, first, second = group_in_review
    monkeypatch.setattr(
        "hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task",
        lambda *args: None,
    )

    PaymentPlanGroupService(group).release_from_vision()

    group.refresh_from_db()
    first.refresh_from_db()
    second.refresh_from_db()
    assert group.status == PaymentPlanGroup.Status.ACCEPTED
    assert first.status == PaymentPlan.Status.ACCEPTED
    assert second.status == PaymentPlan.Status.ACCEPTED
    assert (
        Approval.objects.filter(
            approval_process__payment_plan_group=group,
            type=Approval.FINANCE_RELEASE,
        ).count()
        == 1
    )
    assert first.internal_data["vision"] == {"status": VisionStatus.RELEASED.value}
