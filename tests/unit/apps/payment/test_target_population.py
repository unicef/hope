from unittest.mock import MagicMock

from adminfilters.filters import ChoicesFieldComboFilter
from django.contrib import admin
from django.test import RequestFactory
import pytest

from extras.test_utils.factories import (
    PaymentListFactory,
    PaymentPlanPurposeFactory,
    ProgramFactory,
    TargetPopulationFactory,
    UserFactory,
)
from hope.admin.payment_plan import BasePaymentListAdmin, PaymentListAdmin
from hope.admin.target_population import HIDDEN_FIELDS, TargetPopulationAdmin
from hope.models import PaymentList, TargetPopulation

pytestmark = pytest.mark.django_db


def test_objects_exclude_soft_deleted() -> None:
    plan = PaymentListFactory(status=PaymentList.Status.TP_OPEN)
    deleted = PaymentListFactory(status=PaymentList.Status.TP_OPEN)
    deleted.delete()

    assert list(TargetPopulation.objects.values_list("pk", flat=True)) == [plan.pk]


def test_admin_registered() -> None:
    assert admin.site.is_registered(TargetPopulation)
    assert type(admin.site._registry[TargetPopulation]) is TargetPopulationAdmin


def test_admin_queryset_scoped_to_pre_payment_list_statuses() -> None:
    PaymentListFactory(status=PaymentList.Status.TP_OPEN)
    PaymentListFactory(status=PaymentList.Status.DRAFT)
    PaymentListFactory(status=PaymentList.Status.OPEN)
    PaymentListFactory(status=PaymentList.Status.ACCEPTED)

    request = RequestFactory().get("/")
    request.user = UserFactory()
    model_admin = TargetPopulationAdmin(TargetPopulation, admin.site)

    assert set(model_admin.get_queryset(request).values_list("status", flat=True)) == {
        PaymentList.Status.TP_OPEN.value,
        PaymentList.Status.DRAFT.value,
    }


def test_admin_has_no_add_permission() -> None:
    request = RequestFactory().get("/")
    request.user = UserFactory(is_superuser=True)
    model_admin = TargetPopulationAdmin(TargetPopulation, admin.site)

    assert model_admin.has_add_permission(request) is False


def test_base_admin_frontend_url_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BasePaymentListAdmin(PaymentList, admin.site).frontend_url(PaymentListFactory())


def test_admin_form_hides_payment_list_only_fields() -> None:
    target_population = TargetPopulationFactory()
    request = RequestFactory().get("/")
    request.user = UserFactory(is_superuser=True)
    model_admin = TargetPopulationAdmin(TargetPopulation, admin.site)

    form = model_admin.get_form(request, target_population, change=True)()
    shown_fields = set(form.fields) | set(model_admin.get_readonly_fields(request, target_population))

    assert shown_fields.isdisjoint(HIDDEN_FIELDS + ("plan_type",))


def test_admin_form_limits_status_choices() -> None:
    target_population = TargetPopulationFactory()
    request = RequestFactory().get("/")
    request.user = UserFactory(is_superuser=True)
    model_admin = TargetPopulationAdmin(TargetPopulation, admin.site)

    form = model_admin.get_form(request, target_population, change=True)()

    assert {value for value, _ in form.fields["status"].choices} == {
        status.value for status in PaymentList.PRE_PAYMENT_LIST_STATUSES
    }


def test_admin_hides_background_action_status() -> None:
    assert "background_action_status" in HIDDEN_FIELDS
    assert "background_action_status" not in TargetPopulationAdmin.list_display
    assert ("background_action_status", ChoicesFieldComboFilter) not in TargetPopulationAdmin.list_filter
    assert "background_action_status" in PaymentListAdmin.list_display
    assert ("background_action_status", ChoicesFieldComboFilter) in PaymentListAdmin.list_filter


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
