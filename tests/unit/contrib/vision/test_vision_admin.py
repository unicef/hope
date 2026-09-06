from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from flags.models import FlagState
import pytest

from extras.test_utils.factories import ApprovalProcessFactory, FundsCommitmentGroupFactory, FundsCommitmentItemFactory
from hope.contrib.vision.choices import VisionStatus
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


@pytest.fixture
def vision_admin_context(afghanistan, admin_user, program_cycle, admin_client) -> dict[str, Any]:
    FlagState.objects.get_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        value="True",
    )
    return {
        "business_area": afghanistan,
        "user": admin_user,
        "program_cycle": program_cycle,
        "client": admin_client,
    }


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


@pytest.fixture
def send_failed_payment_plan(vision_admin_context) -> PaymentPlan:
    payment_plan = _create_payment_plan(
        vision_admin_context["business_area"],
        vision_admin_context["user"],
        vision_admin_context["program_cycle"],
    )
    payment_plan.internal_data = {"vision": {"status": VisionStatus.SEND_FAILED.value}}
    payment_plan.save(update_fields=["internal_data"])
    return payment_plan


@pytest.fixture
def waiting_without_send_confirmation_payment_plan(vision_admin_context) -> PaymentPlan:
    payment_plan = _create_payment_plan(
        vision_admin_context["business_area"],
        vision_admin_context["user"],
        vision_admin_context["program_cycle"],
    )
    payment_plan.internal_data = {"vision": {"status": VisionStatus.WAITING_FOR_CALLBACK.value}}
    payment_plan.save(update_fields=["internal_data"])
    return payment_plan


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


def test_manual_fc_item_recovery_shows_warning_and_available_item(
    afghanistan,
    admin_user,
    program_cycle,
    admin_client,
) -> None:
    FlagState.objects.get_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        value="True",
    )
    payment_plan = _create_payment_plan(afghanistan, admin_user, program_cycle)
    payment_plan.internal_data = {
        "vision": {
            "sent": True,
            "status": VisionStatus.FC_NOT_FOUND.value,
        }
    }
    payment_plan.save(update_fields=["internal_data"])
    funds_commitment_group = FundsCommitmentGroupFactory(funds_commitment_number="FC123")
    funds_commitment_item = FundsCommitmentItemFactory(
        funds_commitment_group=funds_commitment_group,
        office=afghanistan,
    )

    change_response = admin_client.get(reverse("admin:payment_paymentplan_change", args=[payment_plan.pk]))
    action_response = admin_client.get(
        reverse("admin:payment_paymentplan_assign_vision_funds_commitment_items", args=[payment_plan.pk])
    )

    assert change_response.status_code == 200
    assert 'id="btn-assign_vision_funds_commitment_items"' in change_response.content.decode()
    assert action_response.status_code == 200
    content = action_response.content.decode()
    assert "Assigning these FC items will automatically release the Payment Plan" in content
    assert "immediately send it to Payment Gateway if" in content
    assert "it is a PG plan" in content
    assert 'id="id_funds_commitment_group"' in content
    assert 'id="vision-fc-options"' in content
    assert "FC123" in content
    assert str(funds_commitment_item.funds_commitment_item) in content


def test_manual_fc_item_recovery_is_available_after_vision_send_failed(
    send_failed_payment_plan,
    admin_client,
) -> None:
    response = admin_client.get(reverse("admin:payment_paymentplan_change", args=[send_failed_payment_plan.pk]))
    action_response = admin_client.get(
        reverse("admin:payment_paymentplan_assign_vision_funds_commitment_items", args=[send_failed_payment_plan.pk])
    )

    assert response.status_code == 200
    assert 'id="btn-assign_vision_funds_commitment_items"' in response.content.decode()
    assert action_response.status_code == 200
    content = action_response.content.decode()
    assert "HOPE could not confirm that this Payment Plan was successfully sent to Vision" in content
    assert "The request may have failed, or" in content
    assert "processing may have stopped before confirmation was recorded" in content


def test_manual_fc_item_recovery_is_available_while_waiting_without_send_confirmation(
    waiting_without_send_confirmation_payment_plan,
    admin_client,
) -> None:
    response = admin_client.get(
        reverse("admin:payment_paymentplan_change", args=[waiting_without_send_confirmation_payment_plan.pk])
    )
    action_response = admin_client.get(
        reverse(
            "admin:payment_paymentplan_assign_vision_funds_commitment_items",
            args=[waiting_without_send_confirmation_payment_plan.pk],
        )
    )

    assert response.status_code == 200
    assert 'id="btn-assign_vision_funds_commitment_items"' in response.content.decode()
    assert action_response.status_code == 200
    content = action_response.content.decode()
    assert "HOPE could not confirm that this Payment Plan was successfully sent to Vision" in content
    assert "The request may have failed, or" in content
    assert "processing may have stopped before confirmation was recorded" in content


@patch("hope.apps.payment.services.payment_plan_services.send_payment_notification_emails_async_task")
@patch("hope.apps.payment.services.payment_plan_services.update_exchange_rate_on_release_payments_async_task")
def test_manual_fc_item_recovery_assigns_items_and_releases_plan(
    mock_exchange_rate_task,
    mock_notification_task,
    vision_admin_context,
    django_capture_on_commit_callbacks,
) -> None:
    payment_plan = _create_payment_plan(
        vision_admin_context["business_area"],
        vision_admin_context["user"],
        vision_admin_context["program_cycle"],
    )
    payment_plan.internal_data = {
        "vision": {
            "sent": True,
            "status": VisionStatus.FC_MISSING.value,
        }
    }
    payment_plan.save(update_fields=["internal_data"])
    ApprovalProcessFactory(payment_plan=payment_plan)
    funds_commitment_group = FundsCommitmentGroupFactory(funds_commitment_number="FC123")
    funds_commitment_item = FundsCommitmentItemFactory(
        funds_commitment_group=funds_commitment_group,
        office=vision_admin_context["business_area"],
    )
    action_url = reverse(
        "admin:payment_paymentplan_assign_vision_funds_commitment_items",
        args=[payment_plan.pk],
    )

    with django_capture_on_commit_callbacks(execute=True):
        response = vision_admin_context["client"].post(
            action_url,
            {
                "funds_commitment_group": funds_commitment_group.pk,
                "funds_commitment_items": [funds_commitment_item.pk],
            },
        )

    assert response.status_code == 302
    payment_plan.refresh_from_db()
    funds_commitment_item.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.ACCEPTED
    assert payment_plan.vision_status == VisionStatus.RELEASED.value
    assert funds_commitment_item.payment_plan_id == payment_plan.pk
    mock_exchange_rate_task.assert_called_once()
    mock_notification_task.assert_called_once()
