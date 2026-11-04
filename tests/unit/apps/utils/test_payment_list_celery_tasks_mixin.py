from django.contrib import messages
from django.core.cache import cache
from django.urls import reverse
from django.utils.crypto import get_random_string
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentListFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.payment.utils import generate_cache_key
from hope.models import PaymentList

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area):
    return ProgramFactory(name="Test ABC", business_area=business_area)


@pytest.fixture
def program_cycle(program):
    return program.cycles.first()


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
def payment_list(admin_user, program_cycle, business_area):
    return PaymentListFactory(
        program_cycle=program_cycle,
        created_by=admin_user["user"],
        business_area=business_area,
    )


@pytest.fixture
def payment_list_url(payment_list):
    return reverse("admin:payment_paymentlist_change", args=[payment_list.id])


@pytest.mark.parametrize(
    ("pp_status", "background_action_status", "html_element"),
    [
        (
            PaymentList.Status.LOCKED,
            PaymentList.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
            'id="btn-restart_importing_entitlements_xlsx_file"',
        ),
        (
            PaymentList.Status.LOCKED,
            PaymentList.BackgroundActionStatus.XLSX_EXPORTING,
            'id="btn-restart_exporting_template_for_entitlement"',
        ),
    ],
)
def test_buttons_are_visible_according_to_status(
    admin_client,
    payment_list,
    payment_list_url,
    pp_status: str,
    background_action_status: str,
    html_element: str,
) -> None:
    payment_list.status = pp_status
    payment_list.background_action_status = background_action_status
    payment_list.save(update_fields=["status", "background_action_status"])

    response = admin_client.get(payment_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert html_element in response.rendered_content


def test_restart_prepare_payment_list_task_success(
    admin_client, admin_user, program_cycle, business_area, enable_is_root
) -> None:
    payment_list = PaymentListFactory(
        status=PaymentList.Status.OPEN,
        program_cycle=program_cycle,
        created_by=admin_user["user"],
        business_area=business_area,
    )
    payment_list.refresh_from_db()
    response = admin_client.post(
        reverse(
            "admin:payment_paymentlist_restart_preparing_payment_list",
            args=[str(payment_list.id)],
        ),
    )
    assert response.status_code == status.HTTP_302_FOUND

    assert (
        list(messages.get_messages(response.wsgi_request))[0].message
        == f"Task restarted for Payment List: {payment_list.unicef_id}"
    )


def test_restart_prepare_payment_list_task_incorrect_status(
    admin_client, admin_user, program_cycle, business_area, enable_is_root
) -> None:
    payment_list = PaymentListFactory(
        status=PaymentList.Status.LOCKED,
        program_cycle=program_cycle,
        created_by=admin_user["user"],
        business_area=business_area,
    )
    payment_list.refresh_from_db()
    response = admin_client.post(
        reverse(
            "admin:payment_paymentlist_restart_preparing_payment_list",
            args=[payment_list.id],
        ),
    )
    assert response.status_code == status.HTTP_302_FOUND

    assert (
        list(messages.get_messages(response.wsgi_request))[0].message
        == f"The Payment List must has the status {PaymentList.Status.OPEN}"
    )


def test_restart_prepare_payment_list_task_already_running(
    admin_client, admin_user, program_cycle, business_area, enable_is_root
) -> None:
    payment_list = PaymentListFactory(
        status=PaymentList.Status.OPEN,
        program_cycle=program_cycle,
        created_by=admin_user["user"],
        business_area=business_area,
    )
    payment_list.refresh_from_db()
    cache_key = generate_cache_key(
        {
            "task_name": "prepare_payment_list_async_task",
            "payment_list_id": str(payment_list.id),
        }
    )
    cache.set(cache_key, True, timeout=600)

    response = admin_client.post(
        reverse(
            "admin:payment_paymentlist_restart_preparing_payment_list",
            args=[payment_list.id],
        ),
    )
    assert response.status_code == status.HTTP_302_FOUND

    assert (
        list(messages.get_messages(response.wsgi_request))[0].message
        == f"Task is already running for Payment List {payment_list.unicef_id}."
    )
    cache.delete(cache_key)
