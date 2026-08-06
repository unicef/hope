from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from flags.models import FlagState
import pytest

from hope.models import PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def program_cycle(afghanistan):
    from extras.test_utils.factories.program import ProgramCycleFactory

    return ProgramCycleFactory(
        program__business_area=afghanistan,
        program__name="Vision Test Program",
    )


@pytest.fixture
def admin_user() -> Any:
    User = get_user_model()  # noqa: N806
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="password",
    )


@pytest.fixture
def admin_client(admin_user: Any) -> Client:
    client = Client()
    client.login(username="admin", password="password")
    return client


def _create_payment_plan(afghanistan, admin_user, program_cycle, status=PaymentPlan.Status.IN_REVIEW):
    from extras.test_utils.factories.payment import PaymentPlanFactory

    afghanistan.vision_integration_active = True
    afghanistan.save(update_fields=["vision_integration_active"])
    return PaymentPlanFactory(
        status=status,
        program_cycle=program_cycle,
        business_area=afghanistan,
        created_by=admin_user,
    )


def test_send_to_vision_button_visible_when_in_review(afghanistan, admin_user, program_cycle, admin_client) -> None:
    FlagState.objects.get_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        value="True",
    )
    pp = _create_payment_plan(afghanistan, admin_user, program_cycle)
    change_url = reverse("admin:payment_paymentplan_change", args=[pp.pk])
    response = admin_client.get(change_url)
    assert response.status_code == 200
    assert 'id="btn-send_to_vision"' in response.content.decode()


def test_send_to_vision_button_hidden_when_open(afghanistan, admin_user, program_cycle, admin_client) -> None:
    FlagState.objects.get_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        value="True",
    )
    pp = _create_payment_plan(afghanistan, admin_user, program_cycle, PaymentPlan.Status.OPEN)
    change_url = reverse("admin:payment_paymentplan_change", args=[pp.pk])
    response = admin_client.get(change_url)
    assert response.status_code == 200
    assert 'id="btn-send_to_vision"' not in response.content.decode()


def test_send_to_vision_button_hidden_when_already_sent(afghanistan, admin_user, program_cycle, admin_client) -> None:
    FlagState.objects.get_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        value="True",
    )
    pp = _create_payment_plan(afghanistan, admin_user, program_cycle)
    pp.internal_data = {"vision": {"sent": True}}
    pp.save(update_fields=["internal_data"])
    change_url = reverse("admin:payment_paymentplan_change", args=[pp.pk])
    response = admin_client.get(change_url)
    assert response.status_code == 200
    assert 'id="btn-send_to_vision"' not in response.content.decode()


def test_send_to_vision_get_returns_confirmation(afghanistan, admin_user, program_cycle, admin_client) -> None:
    FlagState.objects.get_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        value="True",
    )
    pp = _create_payment_plan(afghanistan, admin_user, program_cycle)
    url = reverse("admin:payment_paymentplan_send_to_vision", args=[pp.pk])
    response = admin_client.get(url)
    assert response.status_code == 200
    assert "confirm" in response.content.decode().lower()


@patch("hope.admin.payment_plan.send_payment_plan_to_vision_async_task")
def test_send_to_vision_queues_task(mock_send, afghanistan, admin_user, program_cycle, admin_client) -> None:
    pp = _create_payment_plan(afghanistan, admin_user, program_cycle)
    url = reverse("admin:payment_paymentplan_send_to_vision", args=[pp.pk])
    response = admin_client.post(url)
    assert response.status_code == 302, response.content[:500]
    mock_send.assert_called_once_with(pp, str(admin_user.pk))
