from unittest import mock

from django.contrib import messages
from django.contrib.admin.options import get_content_type_for_model
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.test import override_settings
from django.urls import reverse
from django.utils.crypto import get_random_string
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FileTempFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.admin.utils import PaymentPlanCeleryTasksMixin
from hope.apps.payment.utils import generate_cache_key
from hope.models import PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area):
    return ProgramFactory(name="Test ABC", business_area=business_area)


@pytest.fixture
def program_cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def admin_user():
    password = get_random_string(12)
    user = UserFactory(username="admin")
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save(update_fields=["password", "is_staff", "is_superuser", "is_active"])
    return {"user": user, "password": password}


@pytest.fixture
def admin_client(client, admin_user):
    client.login(username=admin_user["user"].username, password=admin_user["password"])
    return client


@pytest.fixture
def payment_plan(admin_user, program_cycle, business_area):
    return PaymentPlanFactory(
        program_cycle=program_cycle,
        created_by=admin_user["user"],
        business_area=business_area,
    )


@pytest.fixture
def payment_plan_url(payment_plan):
    return reverse("admin:payment_paymentplan_change", args=[payment_plan.id])


@pytest.mark.parametrize(
    ("pp_status", "background_action_status", "html_element"),
    [
        (
            PaymentPlan.Status.LOCKED,
            PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
            'id="btn-restart_importing_entitlements_xlsx_file"',
        ),
        (
            PaymentPlan.Status.ACCEPTED,
            PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
            'id="btn-restart_importing_reconciliation_xlsx_file"',
        ),
        (
            PaymentPlan.Status.LOCKED,
            PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
            'id="btn-restart_exporting_template_for_entitlement"',
        ),
        (
            PaymentPlan.Status.ACCEPTED,
            PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
            'id="btn-restart_exporting_payment_plan_list"',
        ),
    ],
)
def test_buttons_are_visible_according_to_status(
    admin_client,
    payment_plan,
    payment_plan_url,
    pp_status: str,
    background_action_status: str,
    html_element: str,
) -> None:
    payment_plan.status = pp_status
    payment_plan.background_action_status = background_action_status
    payment_plan.save(update_fields=["status", "background_action_status"])

    response = admin_client.get(payment_plan_url)

    assert response.status_code == status.HTTP_200_OK
    assert html_element in response.rendered_content


@override_settings(ROOT_TOKEN="test-token123")
def test_restart_prepare_payment_plan_task_success(admin_client, admin_user, program_cycle, business_area) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        program_cycle=program_cycle,
        created_by=admin_user["user"],
        business_area=business_area,
    )
    payment_plan.refresh_from_db()
    response = admin_client.post(
        reverse(
            "admin:payment_paymentplan_restart_preparing_payment_plan",
            args=[str(payment_plan.id)],
        ),
        HTTP_X_ROOT_TOKEN="test-token123",
    )
    assert response.status_code == status.HTTP_302_FOUND

    assert (
        list(messages.get_messages(response.wsgi_request))[0].message
        == f"Task restarted for Payment Plan: {payment_plan.unicef_id}"
    )


@override_settings(ROOT_TOKEN="test-token123")
def test_restart_prepare_payment_plan_task_incorrect_status(
    admin_client, admin_user, program_cycle, business_area
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        program_cycle=program_cycle,
        created_by=admin_user["user"],
        business_area=business_area,
    )
    payment_plan.refresh_from_db()
    response = admin_client.post(
        reverse(
            "admin:payment_paymentplan_restart_preparing_payment_plan",
            args=[payment_plan.id],
        ),
        HTTP_X_ROOT_TOKEN="test-token123",
    )
    assert response.status_code == status.HTTP_302_FOUND

    assert (
        list(messages.get_messages(response.wsgi_request))[0].message
        == f"The Payment Plan must has the status {PaymentPlan.Status.OPEN}"
    )


@override_settings(ROOT_TOKEN="test-token123")
def test_restart_prepare_payment_plan_task_already_running(
    admin_client, admin_user, program_cycle, business_area
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        program_cycle=program_cycle,
        created_by=admin_user["user"],
        business_area=business_area,
    )
    payment_plan.refresh_from_db()
    cache_key = generate_cache_key(
        {
            "task_name": "prepare_payment_plan_task",
            "payment_plan_id": str(payment_plan.id),
        }
    )
    cache.set(cache_key, True, timeout=600)

    response = admin_client.post(
        reverse(
            "admin:payment_paymentplan_restart_preparing_payment_plan",
            args=[payment_plan.id],
        ),
        HTTP_X_ROOT_TOKEN="test-token123",
    )
    assert response.status_code == status.HTTP_302_FOUND

    assert (
        list(messages.get_messages(response.wsgi_request))[0].message
        == f"Task is already running for Payment Plan {payment_plan.unicef_id}."
    )
    cache.delete(cache_key)


@override_settings(ROOT_TOKEN="test-token123")
def test_restart_importing_reconciliation_xlsx_file(admin_client, admin_user, program_cycle, business_area) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
        program_cycle=program_cycle,
        created_by=admin_user["user"],
        business_area=business_area,
    )
    response = admin_client.post(
        reverse("admin:payment_paymentplan_restart_importing_reconciliation_xlsx_file", args=[payment_plan.id]),
        HTTP_X_ROOT_TOKEN="test-token123",
    )
    assert response.status_code == status.HTTP_302_FOUND

    assert (
        list(messages.get_messages(response.wsgi_request))[-1].message
        == "There is no reconciliation_import_file for this payment plan"
    )

    file_temp = FileTempFactory(
        object_id=str(payment_plan.pk),
        content_type=get_content_type_for_model(payment_plan),
        created_by=admin_user["user"],
        file=ContentFile(b"abc", "Test_123.xlsx"),
    )
    payment_plan.reconciliation_import_file = file_temp
    payment_plan.save(update_fields=["reconciliation_import_file"])
    payment_plan.refresh_from_db()

    with mock.patch("hope.admin.utils.get_task_in_queue_or_running", return_value=None):
        response = admin_client.post(
            reverse("admin:payment_paymentplan_restart_importing_reconciliation_xlsx_file", args=[payment_plan.id]),
            HTTP_X_ROOT_TOKEN="test-token123",
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert (
            list(messages.get_messages(response.wsgi_request))[-1].message
            == f"There is no current {PaymentPlanCeleryTasksMixin.import_payment_plan_payment_list_per_fsp_from_xlsx}"
            f" for this payment plan"
        )
