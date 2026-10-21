from datetime import date
from decimal import Decimal
from typing import Any
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory
from django.urls import reverse
from flags.models import FlagState
import pytest

from extras.test_utils.factories import ApprovalProcessFactory, FundsCommitmentHeaderFactory, FundsCommitmentItemFactory
from hope.admin.funds_commitment_header import FundsCommitmentHeaderAdmin, FundsCommitmentItemInline
from hope.admin.payment_plan import FundsCommitmentHeaderInline as PaymentPlanGroupFundsCommitmentHeaderInline
from hope.contrib.vision.choices import VisionStatus
from hope.contrib.vision.fixtures import FundsCommitmentFactory
from hope.contrib.vision.models import FundsCommitmentHeader
from hope.models import PaymentPlan, PaymentPlanGroup

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
    payment_plan = PaymentPlanFactory(
        status=status,
        program_cycle=program_cycle,
        business_area=afghanistan,
        created_by=admin_user,
    )
    if status == PaymentPlan.Status.IN_REVIEW:
        group = payment_plan.payment_plan_group
        group.status = PaymentPlanGroup.Status.IN_REVIEW
        group.save(update_fields=["status"])
    return payment_plan


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


@pytest.fixture
def payment_plan_created_payment_plan(vision_admin_context) -> PaymentPlan:
    payment_plan = _create_payment_plan(
        vision_admin_context["business_area"],
        vision_admin_context["user"],
        vision_admin_context["program_cycle"],
    )
    payment_plan.internal_data = {
        "vision": {
            "sent": True,
            "status": VisionStatus.PP_CREATED.value,
            "vision_id": "00000110",
        }
    }
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


def test_manual_fc_header_recovery_shows_warning_and_available_header(
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
    funds_commitment_header = FundsCommitmentHeaderFactory(funds_commitment_number="FC123")
    FundsCommitmentItemFactory(
        funds_commitment_header=funds_commitment_header,
        office=afghanistan,
    )

    change_response = admin_client.get(
        reverse("admin:payment_paymentplangroup_change", args=[payment_plan.payment_plan_group_id])
    )
    action_response = admin_client.get(
        reverse(
            "admin:payment_paymentplangroup_assign_vision_funds_commitment_headers",
            args=[payment_plan.payment_plan_group_id],
        )
    )

    assert change_response.status_code == 200
    assert 'id="btn-assign_vision_funds_commitment_headers"' in change_response.content.decode()
    assert action_response.status_code == 200
    content = " ".join(action_response.content.decode().split())
    assert "Assigning these FC headers to the Payment Plan Group will automatically release all pending" in content
    assert "immediately send each Payment Gateway plan to Payment Gateway" in content
    assert 'id="id_payment_plan"' not in content
    assert 'id="id_funds_commitment_headers"' in content
    assert "FC123" in content


def test_manual_fc_header_recovery_is_available_after_vision_send_failed(
    send_failed_payment_plan,
    admin_client,
) -> None:
    response = admin_client.get(
        reverse("admin:payment_paymentplangroup_change", args=[send_failed_payment_plan.payment_plan_group_id])
    )
    action_response = admin_client.get(
        reverse(
            "admin:payment_paymentplangroup_assign_vision_funds_commitment_headers",
            args=[send_failed_payment_plan.payment_plan_group_id],
        )
    )

    assert response.status_code == 200
    assert 'id="btn-assign_vision_funds_commitment_headers"' in response.content.decode()
    assert action_response.status_code == 200
    content = action_response.content.decode()
    assert "every Payment Plan in this group" in content
    assert "A request may have" in content
    assert "processing may have stopped before confirmation was recorded" in content


def test_manual_fc_header_recovery_is_available_while_waiting_without_send_confirmation(
    waiting_without_send_confirmation_payment_plan,
    admin_client,
) -> None:
    response = admin_client.get(
        reverse(
            "admin:payment_paymentplangroup_change",
            args=[waiting_without_send_confirmation_payment_plan.payment_plan_group_id],
        )
    )
    action_response = admin_client.get(
        reverse(
            "admin:payment_paymentplangroup_assign_vision_funds_commitment_headers",
            args=[waiting_without_send_confirmation_payment_plan.payment_plan_group_id],
        )
    )

    assert response.status_code == 200
    assert 'id="btn-assign_vision_funds_commitment_headers"' in response.content.decode()
    assert action_response.status_code == 200
    content = action_response.content.decode()
    assert "every Payment Plan in this group" in content
    assert "A request may have" in content
    assert "processing may have stopped before confirmation was recorded" in content


def test_manual_fc_header_recovery_does_not_warn_after_payment_plan_created_acknowledgement(
    payment_plan_created_payment_plan,
    admin_client,
) -> None:
    action_response = admin_client.get(
        reverse(
            "admin:payment_paymentplangroup_assign_vision_funds_commitment_headers",
            args=[payment_plan_created_payment_plan.payment_plan_group_id],
        )
    )

    assert action_response.status_code == 200
    content = action_response.content.decode()
    assert "HOPE could not confirm that every Payment Plan in this group" not in content


@pytest.fixture
def recoverable_group_with_two_headers(vision_admin_context):
    payment_plan = _create_payment_plan(
        vision_admin_context["business_area"],
        vision_admin_context["user"],
        vision_admin_context["program_cycle"],
    )
    payment_plan.internal_data = {
        "vision": {
            "sent": True,
            "status": VisionStatus.FC_NOT_FOUND.value,
        }
    }
    payment_plan.save(update_fields=["internal_data"])
    from extras.test_utils.factories.payment import PaymentPlanFactory

    sibling_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.IN_REVIEW,
        program_cycle=vision_admin_context["program_cycle"],
        payment_plan_group=payment_plan.payment_plan_group,
        business_area=vision_admin_context["business_area"],
        created_by=vision_admin_context["user"],
        internal_data={"vision": {"sent": True, "status": VisionStatus.FC_NOT_FOUND.value}},
    )
    ApprovalProcessFactory(payment_plan_group=payment_plan.payment_plan_group)
    funds_commitment_header = FundsCommitmentHeaderFactory(funds_commitment_number="FC123")
    second_header = FundsCommitmentHeaderFactory(funds_commitment_number="FC456")
    FundsCommitmentItemFactory(
        funds_commitment_header=funds_commitment_header,
        office=vision_admin_context["business_area"],
    )
    FundsCommitmentItemFactory(funds_commitment_header=second_header, office=vision_admin_context["business_area"])
    return payment_plan, sibling_plan, funds_commitment_header, second_header


@pytest.fixture
def group_with_unrecoverable_pending_plan(recoverable_group_with_two_headers):
    payment_plan, sibling_plan, funds_commitment_header, second_header = recoverable_group_with_two_headers
    sibling_plan.internal_data = {"vision": {"status": VisionStatus.NOT_SENT.value}}
    sibling_plan.save(update_fields=["internal_data"])
    return payment_plan, sibling_plan, funds_commitment_header, second_header


def test_manual_fc_header_recovery_waits_for_every_pending_plan(
    vision_admin_context, group_with_unrecoverable_pending_plan, django_assert_num_queries
) -> None:
    payment_plan, sibling_plan, funds_commitment_header, second_header = group_with_unrecoverable_pending_plan
    group = payment_plan.payment_plan_group
    action_url = reverse("admin:payment_paymentplangroup_assign_vision_funds_commitment_headers", args=[group.pk])

    change_response = vision_admin_context["client"].get(
        reverse("admin:payment_paymentplangroup_change", args=[group.pk])
    )
    action_response = vision_admin_context["client"].post(
        action_url,
        {"funds_commitment_headers": [funds_commitment_header.pk, second_header.pk]},
    )

    assert 'id="btn-assign_vision_funds_commitment_headers"' not in change_response.content.decode()
    assert action_response.status_code == 200
    assert "Vision recovery is no longer available" in action_response.content.decode()
    payment_plan.refresh_from_db()
    sibling_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.IN_REVIEW
    assert sibling_plan.status == PaymentPlan.Status.IN_REVIEW
    with django_assert_num_queries(1):
        assert not group.funds_commitment_headers.exists()


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
@patch("hope.apps.payment.services.payment_plan_services.send_payment_notification_emails_async_task")
@patch("hope.apps.payment.services.payment_plan_services.update_exchange_rate_on_release_payments_async_task")
def test_manual_fc_header_recovery_assigns_multiple_headers_and_releases_group(
    mock_exchange_rate_task,
    mock_notification_task,
    mock_group_notification_task,
    vision_admin_context,
    recoverable_group_with_two_headers,
    django_capture_on_commit_callbacks,
) -> None:
    payment_plan, sibling_plan, funds_commitment_header, second_header = recoverable_group_with_two_headers
    action_url = reverse(
        "admin:payment_paymentplangroup_assign_vision_funds_commitment_headers",
        args=[payment_plan.payment_plan_group_id],
    )

    with django_capture_on_commit_callbacks(execute=True):
        response = vision_admin_context["client"].post(
            action_url,
            {
                "funds_commitment_headers": [funds_commitment_header.pk, second_header.pk],
            },
        )

    assert response.status_code == 302
    payment_plan.refresh_from_db()
    sibling_plan.refresh_from_db()
    payment_plan.payment_plan_group.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.ACCEPTED
    assert sibling_plan.status == PaymentPlan.Status.ACCEPTED
    assert payment_plan.payment_plan_group.status == PaymentPlanGroup.Status.ACCEPTED
    assert payment_plan.vision_status == VisionStatus.RELEASED.value
    assert sibling_plan.vision_status == VisionStatus.RELEASED.value
    assert set(payment_plan.payment_plan_group.funds_commitment_headers.all()) == {
        funds_commitment_header,
        second_header,
    }
    assert mock_exchange_rate_task.call_count == 2
    assert mock_notification_task.call_count == 2
    mock_group_notification_task.assert_called_once()


@pytest.fixture
def funds_commitment_header_for_admin(afghanistan) -> FundsCommitmentHeader:
    FundsCommitmentFactory(
        rec_serial_number=100,
        funds_commitment_number="FC123",
        vendor_id="VENDOR-1",
        posting_date=date(2026, 9, 1),
        document_reference="REFERENCE-1",
        fc_status="O",
        currency_code="USD",
        commitment_amount_local=Decimal("100.25"),
        commitment_amount_usd=Decimal("100.50"),
    )
    return FundsCommitmentHeader.objects.get(funds_commitment_number="FC123")


@pytest.fixture
def payment_plan_with_funds_commitment_header(
    vision_admin_context,
    funds_commitment_header_for_admin: FundsCommitmentHeader,
) -> tuple[PaymentPlan, FundsCommitmentHeader]:
    payment_plan = _create_payment_plan(
        vision_admin_context["business_area"],
        vision_admin_context["user"],
        vision_admin_context["program_cycle"],
    )
    funds_commitment_header_for_admin.payment_plan_groups.add(payment_plan.payment_plan_group)
    return payment_plan, funds_commitment_header_for_admin


def test_funds_commitment_header_admin_displays_derived_fields(
    admin_user,
    funds_commitment_header_for_admin: FundsCommitmentHeader,
    django_assert_num_queries,
) -> None:
    request = RequestFactory().get("/")
    request.user = admin_user
    model_admin = FundsCommitmentHeaderAdmin(FundsCommitmentHeader, admin.site)

    with django_assert_num_queries(1):
        header = model_admin.get_queryset(request).get(pk=funds_commitment_header_for_admin.pk)

    assert model_admin.list_display == (
        "funds_commitment_number",
        "vendor_id",
        "posting_date",
        "document_reference",
        "fc_status",
        "total_amount_usd",
        "total_amount_local",
        "currency",
    )
    assert model_admin.readonly_fields == model_admin.list_display[1:]
    assert header.vendor_id == "VENDOR-1"
    assert header.posting_date == date(2026, 9, 1)
    assert header.document_reference == "REFERENCE-1"
    assert header.fc_status == "O"
    assert model_admin.total_amount_usd(header) == Decimal("100.50")
    assert model_admin.total_amount_local(header) == Decimal("100.25")
    assert header.currency == "USD"


def test_payment_plan_group_funds_commitment_header_inline_displays_details_and_link(
    admin_user,
    payment_plan_with_funds_commitment_header: tuple[PaymentPlan, FundsCommitmentHeader],
    django_assert_num_queries,
) -> None:
    payment_plan, header = payment_plan_with_funds_commitment_header
    request = RequestFactory().get("/")
    request.user = admin_user
    inline = PaymentPlanGroupFundsCommitmentHeaderInline(type(payment_plan.payment_plan_group), admin.site)

    with django_assert_num_queries(2):
        assignment = inline.get_queryset(request).get(
            paymentplangroup=payment_plan.payment_plan_group,
            fundscommitmentheader=header,
        )

    with django_assert_num_queries(0):
        header_link = inline.funds_commitment_number(assignment)
        assert reverse("admin:vision_fundscommitmentheader_change", args=[header.pk]) in header_link
        assert header.funds_commitment_number in header_link
        assert inline.vendor_id(assignment) == "VENDOR-1"
        assert inline.posting_date(assignment) == date(2026, 9, 1)
        assert inline.document_reference(assignment) == "REFERENCE-1"
        assert inline.fc_status(assignment) == "O"
        assert inline.total_amount_usd(assignment) == Decimal("100.50")
        assert inline.total_amount_local(assignment) == Decimal("100.25")
        assert inline.currency(assignment) == "USD"


def test_funds_commitment_item_inline_remains_unchanged() -> None:
    assert FundsCommitmentItemInline.fields == (
        "rec_serial_number",
        "funds_commitment_item",
        "office",
        "fc_status",
        "commitment_amount_local",
        "commitment_amount_usd",
        "total_open_amount_local",
        "total_open_amount_usd",
    )
