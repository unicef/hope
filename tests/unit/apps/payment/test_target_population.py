from unittest.mock import MagicMock

from django.contrib import admin
from django.test import RequestFactory
import pytest

from extras.test_utils.factories import (
    PaymentPlanFactory,
    PaymentPlanPurposeFactory,
    ProgramFactory,
    TargetPopulationFactory,
    UserFactory,
)
from hope.admin.payment_plan import BasePaymentPlanAdmin
from hope.admin.target_population import HIDDEN_FIELDS, TargetPopulationAdmin
from hope.models import PaymentPlan, TargetPopulation

pytestmark = pytest.mark.django_db


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
    PaymentPlanFactory(status=PaymentPlan.Status.DRAFT)
    PaymentPlanFactory(status=PaymentPlan.Status.OPEN)
    PaymentPlanFactory(status=PaymentPlan.Status.ACCEPTED)

    request = RequestFactory().get("/")
    request.user = UserFactory()
    model_admin = TargetPopulationAdmin(TargetPopulation, admin.site)

    assert set(model_admin.get_queryset(request).values_list("status", flat=True)) == {
        PaymentPlan.Status.TP_OPEN.value,
        PaymentPlan.Status.DRAFT.value,
    }


def test_admin_has_no_add_permission() -> None:
    request = RequestFactory().get("/")
    request.user = UserFactory(is_superuser=True)
    model_admin = TargetPopulationAdmin(TargetPopulation, admin.site)

    assert model_admin.has_add_permission(request) is False


def test_base_admin_frontend_url_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BasePaymentPlanAdmin(PaymentPlan, admin.site).frontend_url(PaymentPlanFactory())


def test_admin_form_hides_payment_plan_only_fields() -> None:
    target_population = TargetPopulationFactory()
    request = RequestFactory().get("/")
    request.user = UserFactory(is_superuser=True)
    model_admin = TargetPopulationAdmin(TargetPopulation, admin.site)

    form = model_admin.get_form(request, target_population, change=True)()
    shown_fields = set(form.fields) | set(model_admin.get_readonly_fields(request, target_population))

    assert shown_fields.isdisjoint(HIDDEN_FIELDS + ("plan_type",))


def test_admin_form_scopes_payment_plan_purposes_to_program() -> None:
    target_population = TargetPopulationFactory()
    purpose = target_population.program_cycle.program.payment_plan_purposes.get()
    other_program = ProgramFactory()
    other_purpose = PaymentPlanPurposeFactory()
    other_program.payment_plan_purposes.add(other_purpose)
    request = RequestFactory().get("/")
    request.resolver_match = MagicMock()
    request.resolver_match.kwargs = {"object_id": str(target_population.pk)}
    request.user = UserFactory(is_superuser=True)
    model_admin = TargetPopulationAdmin(TargetPopulation, admin.site)

    form = model_admin.get_form(request, target_population, change=True)()

    assert list(form.fields["payment_plan_purposes"].queryset) == [purpose]
