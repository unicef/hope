from datetime import timezone as dt_timezone
from decimal import Decimal
import json
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from flags.models import FlagState
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    ApprovalFactory,
    ApprovalProcessFactory,
    BusinessAreaFactory,
    PartnerFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.factories.core import CurrencyFactory
from extras.test_utils.factories.payment import FinancialServiceProviderFactory
from hope.apps.account.permissions import Permissions
from hope.models import Approval, PaymentPlan, PaymentPlanGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def managerial_context(api_client: Callable, business_area: Any) -> dict[str, Any]:
    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    program1 = ProgramFactory(business_area=business_area, cycle=False)
    program2 = ProgramFactory(business_area=business_area, cycle=False)
    cycle1 = ProgramCycleFactory(program=program1, title="Cycle 1")
    cycle2 = ProgramCycleFactory(program=program2, title="Cycle 2")
    group1 = PaymentPlanGroupFactory(
        cycle=cycle1,
        name="Group One",
        status=PaymentPlanGroup.Status.IN_APPROVAL,
        financial_service_provider=FinancialServiceProviderFactory(name="FSP One"),
        currency=CurrencyFactory(code="PLN", name="Polish Zloty"),
    )
    group2 = PaymentPlanGroupFactory(cycle=cycle2, name="Group Two", status=PaymentPlanGroup.Status.IN_APPROVAL)
    group3 = PaymentPlanGroupFactory(cycle=cycle2, name="Group Three", status=PaymentPlanGroup.Status.OPEN)
    group1.unicef_id = "PPG-MAN-001"
    group1.save(update_fields=["unicef_id"])
    group2.unicef_id = "PPG-MAN-002"
    group2.save(update_fields=["unicef_id"])
    group3.unicef_id = "PPG-MAN-003"
    group3.save(update_fields=["unicef_id"])
    PaymentPlanFactory(
        program_cycle=cycle1,
        payment_plan_group=group1,
        business_area=business_area,
        status=PaymentPlan.Status.IN_APPROVAL,
        total_households_count=3,
        total_entitled_quantity_usd=Decimal("100.00"),
    )
    PaymentPlanFactory(
        program_cycle=cycle1,
        payment_plan_group=group1,
        business_area=business_area,
        status=PaymentPlan.Status.IN_APPROVAL,
        total_households_count=2,
        total_entitled_quantity_usd=Decimal("50.00"),
    )
    PaymentPlanFactory(
        program_cycle=cycle2,
        payment_plan_group=group2,
        business_area=business_area,
        status=PaymentPlan.Status.IN_APPROVAL,
    )
    PaymentPlanFactory(
        program_cycle=cycle2, payment_plan_group=group3, business_area=business_area, status=PaymentPlan.Status.OPEN
    )
    return {
        "partner": partner,
        "user": user,
        "client": api_client(user),
        "business_area": business_area,
        "program1": program1,
        "program2": program2,
        "group1": group1,
        "group2": group2,
        "group3": group3,
        "url": reverse("api:payments:payment-plans-managerial-list", kwargs={"business_area_slug": business_area.slug}),
        "bulk_url": reverse(
            "api:payments:payment-plans-managerial-bulk-action", kwargs={"business_area_slug": business_area.slug}
        ),
    }


@pytest.fixture
def vision_managerial_context(managerial_context: dict[str, Any]) -> dict[str, Any]:
    group = managerial_context["group1"]
    group.status = PaymentPlanGroup.Status.IN_REVIEW
    group.save(update_fields=["status"])
    group.payment_plans.update(status=PaymentPlan.Status.IN_REVIEW)
    managerial_context["business_area"].vision_integration_active = True
    managerial_context["business_area"].save(update_fields=["vision_integration_active"])
    FlagState.objects.get_or_create(name="VISION_INTEGRATION_ACTIVE", condition="boolean", value="True")
    return managerial_context


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([], status.HTTP_403_FORBIDDEN),
        ([Permissions.PAYMENT_VIEW_LIST_MANAGERIAL], status.HTTP_200_OK),
    ],
)
def test_list_groups_permission(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(
        managerial_context["user"], permissions, managerial_context["business_area"], managerial_context["program1"]
    )

    response = managerial_context["client"].get(managerial_context["url"])

    assert response.status_code == expected_status


def test_list_groups_shows_only_programmes_the_user_may_see(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    create_partner_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        managerial_context["user"],
        [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        program=managerial_context["program1"],
    )

    response = managerial_context["client"].get(managerial_context["url"])

    assert response.status_code == status.HTTP_200_OK
    assert [group["unicef_id"] for group in response.json()["results"]] == ["PPG-MAN-001"]

    with TestCase.captureOnCommitCallbacks(execute=True):
        create_partner_role_with_permissions(
            managerial_context["partner"],
            [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
            managerial_context["business_area"],
            program=managerial_context["program2"],
        )

    response = managerial_context["client"].get(managerial_context["url"])

    assert response.status_code == status.HTTP_200_OK
    assert {group["unicef_id"] for group in response.json()["results"]} == {"PPG-MAN-001", "PPG-MAN-002"}


def test_list_groups_row_carries_programme_totals_and_configuration(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        managerial_context["user"],
        [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        managerial_context["program1"],
    )

    response = managerial_context["client"].get(managerial_context["url"])

    assert response.status_code == status.HTTP_200_OK
    row = response.json()["results"][0]
    assert row["name"] == "Group One"
    assert row["status"] == PaymentPlanGroup.Status.IN_APPROVAL
    assert row["status_display"] == "In Approval"
    assert row["program"] == managerial_context["program1"].name
    assert row["program_code"] == managerial_context["program1"].code
    assert row["cycle_title"] == "Cycle 1"
    assert row["financial_service_provider"] == "FSP One"
    assert row["currency"] == "PLN"
    assert row["payment_plans_count"] == 2
    assert row["total_households_count"] == 5
    assert row["total_entitled_quantity_usd"] == "150.00"


def test_list_groups_is_cached_by_etag(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        managerial_context["user"],
        [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        managerial_context["program1"],
    )

    with CaptureQueriesContext(connection) as first_call:
        response = managerial_context["client"].get(managerial_context["url"])
    etag = response.headers["etag"]
    with CaptureQueriesContext(connection) as second_call:
        cached_response = managerial_context["client"].get(managerial_context["url"])

    assert response.status_code == status.HTTP_200_OK
    assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
    assert cached_response.headers["etag"] == etag
    assert cached_response.json() == response.json()
    assert len(second_call.captured_queries) < len(first_call.captured_queries)


def test_list_groups_drops_group_once_it_leaves_the_approval_stages(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        managerial_context["user"],
        [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        managerial_context["program1"],
    )
    managerial_context["client"].get(managerial_context["url"])

    with TestCase.captureOnCommitCallbacks(execute=True):
        managerial_context["group1"].status = PaymentPlanGroup.Status.FINISHED
        managerial_context["group1"].save(update_fields=["status"])
    response = managerial_context["client"].get(managerial_context["url"])

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"] == []


def test_list_groups_approval_process_data(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    approval_process = ApprovalProcessFactory(
        payment_plan_group=managerial_context["group1"],
        sent_for_approval_date=timezone.datetime(2021, 1, 1, 0, 0, 0, tzinfo=dt_timezone.utc),
        sent_for_approval_by=managerial_context["user"],
    )
    approval_approval = ApprovalFactory(approval_process=approval_process, type=Approval.APPROVAL)
    approval_authorization = ApprovalFactory(approval_process=approval_process, type=Approval.AUTHORIZATION)
    approval_release = ApprovalFactory(approval_process=approval_process, type=Approval.FINANCE_RELEASE)
    create_user_role_with_permissions(
        managerial_context["user"],
        [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        managerial_context["program1"],
    )
    group = managerial_context["group1"]

    response = managerial_context["client"].get(managerial_context["url"])

    assert response.status_code == status.HTTP_200_OK
    row = response.json()["results"][0]
    assert row["last_approval_process_date"] == approval_process.sent_for_approval_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert row["last_approval_process_by"] == str(approval_process.sent_for_approval_by)

    with TestCase.captureOnCommitCallbacks(execute=True):
        group.status = PaymentPlanGroup.Status.IN_AUTHORIZATION
        group.save(update_fields=["status"])
    row = managerial_context["client"].get(managerial_context["url"]).json()["results"][0]
    assert row["last_approval_process_date"] == approval_approval.created_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert row["last_approval_process_by"] == str(approval_approval.created_by)

    with TestCase.captureOnCommitCallbacks(execute=True):
        group.status = PaymentPlanGroup.Status.IN_REVIEW
        group.save(update_fields=["status"])
    row = managerial_context["client"].get(managerial_context["url"]).json()["results"][0]
    assert row["last_approval_process_date"] == approval_authorization.created_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert row["last_approval_process_by"] == str(approval_authorization.created_by)

    with TestCase.captureOnCommitCallbacks(execute=True):
        group.status = PaymentPlanGroup.Status.ACCEPTED
        group.save(update_fields=["status"])
    row = managerial_context["client"].get(managerial_context["url"]).json()["results"][0]
    assert row["last_approval_process_date"] == approval_release.created_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert row["last_approval_process_by"] == str(approval_release.created_by)


def test_bulk_approve_moves_groups_and_their_plans(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    create_partner_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        managerial_context["user"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE, Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        managerial_context["program1"],
    )
    create_partner_role_with_permissions(
        managerial_context["partner"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE, Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        managerial_context["program2"],
    )
    ApprovalProcessFactory(payment_plan_group=managerial_context["group1"])
    ApprovalProcessFactory(payment_plan_group=managerial_context["group2"])
    group1, group2 = managerial_context["group1"], managerial_context["group2"]

    response = managerial_context["client"].post(
        managerial_context["bulk_url"],
        data={"ids": [group1.id, group2.id], "action": PaymentPlan.Action.APPROVE.value, "comment": "Test comment"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    group1.refresh_from_db()
    group2.refresh_from_db()
    assert group1.status == PaymentPlanGroup.Status.IN_AUTHORIZATION
    assert group2.status == PaymentPlanGroup.Status.IN_AUTHORIZATION
    assert set(group1.payment_plans.values_list("status", flat=True)) == {PaymentPlan.Status.IN_AUTHORIZATION}
    assert group1.approval_process.first().approvals.get().comment == "Test comment"


def test_bulk_release_skips_vision_managed_group(
    vision_managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    group = vision_managerial_context["group1"]
    assert all(payment_plan.vision_managed for payment_plan in group.payment_plans.all())
    create_user_role_with_permissions(
        vision_managerial_context["user"],
        [Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW, Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        vision_managerial_context["business_area"],
        vision_managerial_context["program1"],
    )

    response = vision_managerial_context["client"].post(
        vision_managerial_context["bulk_url"], data={"ids": [group.id], "action": PaymentPlan.Action.REVIEW.value}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    group.refresh_from_db()
    assert group.status == PaymentPlanGroup.Status.IN_REVIEW


def test_bulk_action_rejects_unsupported_action(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        managerial_context["user"],
        [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        managerial_context["program1"],
    )

    response = managerial_context["client"].post(
        managerial_context["bulk_url"],
        data={"ids": [managerial_context["group1"].id], "action": PaymentPlan.Action.MARK_READY_FOR_CLOSURE.value},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "action" in response.json()
    managerial_context["group1"].refresh_from_db()
    assert managerial_context["group1"].status == PaymentPlanGroup.Status.IN_APPROVAL


def test_bulk_action_without_stage_permission_returns_403_and_changes_nothing(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    create_partner_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        managerial_context["user"],
        [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        managerial_context["program1"],
    )
    create_partner_role_with_permissions(
        managerial_context["partner"],
        [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        managerial_context["program2"],
    )
    ApprovalProcessFactory(payment_plan_group=managerial_context["group1"])
    ApprovalProcessFactory(payment_plan_group=managerial_context["group2"])
    group1, group2 = managerial_context["group1"], managerial_context["group2"]

    response = managerial_context["client"].post(
        managerial_context["bulk_url"],
        data={"ids": [group1.id, group2.id], "action": PaymentPlan.Action.APPROVE.value, "comment": "Test comment"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["required_permissions"] == [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.value]
    group1.refresh_from_db()
    group2.refresh_from_db()
    assert group1.status == PaymentPlanGroup.Status.IN_APPROVAL
    assert group2.status == PaymentPlanGroup.Status.IN_APPROVAL


def test_bulk_action_ignores_groups_of_another_business_area(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        managerial_context["user"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE, Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        managerial_context["program1"],
    )
    other_group = PaymentPlanGroupFactory(status=PaymentPlanGroup.Status.IN_APPROVAL)
    ApprovalProcessFactory(payment_plan_group=other_group)

    response = managerial_context["client"].post(
        managerial_context["bulk_url"], data={"ids": [other_group.id], "action": PaymentPlan.Action.APPROVE.value}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    other_group.refresh_from_db()
    assert other_group.status == PaymentPlanGroup.Status.IN_APPROVAL
