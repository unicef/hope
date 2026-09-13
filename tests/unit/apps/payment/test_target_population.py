from django.contrib import admin
from django.test import RequestFactory
import pytest

from extras.test_utils.factories import PaymentPlanFactory, UserFactory
from hope.admin.target_population import TargetPopulationAdmin
from hope.models import PaymentPlan, TargetPopulation

pytestmark = pytest.mark.django_db


def test_objects_include_only_pre_payment_plan_statuses() -> None:
    PaymentPlanFactory(status=PaymentPlan.Status.TP_OPEN)
    PaymentPlanFactory(status=PaymentPlan.Status.DRAFT)
    PaymentPlanFactory(status=PaymentPlan.Status.OPEN)
    PaymentPlanFactory(status=PaymentPlan.Status.ACCEPTED)

    assert set(TargetPopulation.objects.values_list("status", flat=True)) == {
        PaymentPlan.Status.TP_OPEN.value,
        PaymentPlan.Status.DRAFT.value,
    }


def test_objects_exclude_soft_deleted() -> None:
    plan = PaymentPlanFactory(status=PaymentPlan.Status.TP_OPEN)
    deleted = PaymentPlanFactory(status=PaymentPlan.Status.TP_OPEN)
    deleted.delete()

    assert list(TargetPopulation.objects.values_list("pk", flat=True)) == [plan.pk]


def test_admin_registered() -> None:
    assert admin.site.is_registered(TargetPopulation)
    assert type(admin.site._registry[TargetPopulation]) is TargetPopulationAdmin


def test_admin_queryset_scoped_to_pre_payment_plan_statuses() -> None:
    PaymentPlanFactory(status=PaymentPlan.Status.TP_OPEN)
    PaymentPlanFactory(status=PaymentPlan.Status.ACCEPTED)

    request = RequestFactory().get("/")
    request.user = UserFactory()
    model_admin = TargetPopulationAdmin(TargetPopulation, admin.site)

    assert set(model_admin.get_queryset(request).values_list("status", flat=True)) == {
        PaymentPlan.Status.TP_OPEN.value,
    }


def test_admin_has_no_add_permission() -> None:
    request = RequestFactory().get("/")
    request.user = UserFactory(is_superuser=True)
    model_admin = TargetPopulationAdmin(TargetPopulation, admin.site)

    assert model_admin.has_add_permission(request) is False
