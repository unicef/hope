from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from flags.models import FlagState
import pytest

from hope.contrib.vision.api import VisionAPIError, VisionAPIMissingCredentialsError
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


def _create_payment_plan(afghanistan, admin_user, program_cycle, status=PaymentPlan.Status.ACCEPTED):
    from extras.test_utils.factories.payment import PaymentPlanFactory

    return PaymentPlanFactory(
        status=status,
        program_cycle=program_cycle,
        business_area=afghanistan,
        created_by=admin_user,
    )


def test_send_to_vision_button_visible_when_accepted(afghanistan, admin_user, program_cycle, admin_client) -> None:
    FlagState.objects.get_or_create(
        name="SHOW_SEND_TO_VISION_BUTTON",
        condition="boolean",
        value="True",
    )
    pp = _create_payment_plan(afghanistan, admin_user, program_cycle, PaymentPlan.Status.ACCEPTED)
    change_url = reverse("admin:payment_paymentplan_change", args=[pp.pk])
    response = admin_client.get(change_url)
    assert response.status_code == 200
    assert 'id="btn-send_to_vision"' in response.content.decode()


def test_send_to_vision_button_hidden_when_open(afghanistan, admin_user, program_cycle, admin_client) -> None:
    FlagState.objects.get_or_create(
        name="SHOW_SEND_TO_VISION_BUTTON",
        condition="boolean",
        value="True",
    )
    pp = _create_payment_plan(afghanistan, admin_user, program_cycle, PaymentPlan.Status.OPEN)
    change_url = reverse("admin:payment_paymentplan_change", args=[pp.pk])
    response = admin_client.get(change_url)
    assert response.status_code == 200
    assert 'id="btn-send_to_vision"' not in response.content.decode()


def test_send_to_vision_get_returns_confirmation(afghanistan, admin_user, program_cycle, admin_client) -> None:
    FlagState.objects.get_or_create(
        name="SHOW_SEND_TO_VISION_BUTTON",
        condition="boolean",
        value="True",
    )
    pp = _create_payment_plan(afghanistan, admin_user, program_cycle, PaymentPlan.Status.ACCEPTED)
    url = reverse("admin:payment_paymentplan_send_to_vision", args=[pp.pk])
    response = admin_client.get(url)
    assert response.status_code == 200
    assert "confirm" in response.content.decode().lower()


@patch("hope.contrib.vision.api.VisionAPI.send_payment_plan")
def test_send_to_vision_calls_api(mock_send, afghanistan, admin_user, program_cycle, admin_client, settings) -> None:
    mock_send.return_value = {"status": "ok", "messageId": "test-msg-id"}
    pp = _create_payment_plan(afghanistan, admin_user, program_cycle, PaymentPlan.Status.ACCEPTED)
    url = reverse("admin:payment_paymentplan_send_to_vision", args=[pp.pk])
    settings.VISION_API_URL = "http://fake.vision.test/"
    response = admin_client.post(url)
    assert response.status_code == 302, response.content[:500]
    mock_send.assert_called_once_with(pp)


@patch("hope.contrib.vision.api.VisionAPI.send_payment_plan")
def test_send_to_vision_handles_api_error(
    mock_send, afghanistan, admin_user, program_cycle, admin_client, settings
) -> None:
    mock_send.side_effect = VisionAPIError("boom")
    pp = _create_payment_plan(afghanistan, admin_user, program_cycle, PaymentPlan.Status.ACCEPTED)
    url = reverse("admin:payment_paymentplan_send_to_vision", args=[pp.pk])
    settings.VISION_API_URL = "http://fake.vision.test/"
    response = admin_client.post(url)
    assert response.status_code == 302
    mock_send.assert_called_once_with(pp)


@patch("hope.contrib.vision.api.VisionAPI.send_payment_plan")
def test_send_to_vision_handles_missing_creds(
    mock_send, afghanistan, admin_user, program_cycle, admin_client, settings
) -> None:
    mock_send.side_effect = VisionAPIMissingCredentialsError("no creds")
    pp = _create_payment_plan(afghanistan, admin_user, program_cycle, PaymentPlan.Status.ACCEPTED)
    url = reverse("admin:payment_paymentplan_send_to_vision", args=[pp.pk])
    settings.VISION_API_URL = "http://fake.vision.test/"
    response = admin_client.post(url)
    assert response.status_code == 302
    mock_send.assert_called_once_with(pp)
