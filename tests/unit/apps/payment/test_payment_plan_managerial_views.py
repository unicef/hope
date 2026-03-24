from datetime import timezone as dt_timezone
import json
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    ApprovalFactory,
    ApprovalProcessFactory,
    BusinessAreaFactory,
    PartnerFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.api.views import PaymentPlanManagerialViewSet
from hope.models import Approval, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def managerial_context(
    api_client: Callable,
    business_area: Any,
) -> dict[str, Any]:
    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)
    program1 = ProgramFactory(business_area=business_area)
    program2 = ProgramFactory(business_area=business_area)
    cycle1 = ProgramCycleFactory(program=program1, title="Cycle 1")
    cycle2 = ProgramCycleFactory(program=program2, title="Cycle 2")
    payment_plan1 = PaymentPlanFactory(
        program_cycle=cycle1,
        business_area=business_area,
        status=PaymentPlan.Status.IN_APPROVAL,
        created_by=user,
    )
    payment_plan2 = PaymentPlanFactory(
        program_cycle=cycle2,
        business_area=business_area,
        status=PaymentPlan.Status.IN_APPROVAL,
        created_by=user,
    )
    payment_plan3 = PaymentPlanFactory(
        program_cycle=cycle2,
        business_area=business_area,
        status=PaymentPlan.Status.OPEN,
        created_by=user,
    )
    payment_plan1.unicef_id = "PP-MAN-001"
    payment_plan1.save(update_fields=["unicef_id"])
    payment_plan2.unicef_id = "PP-MAN-002"
    payment_plan2.save(update_fields=["unicef_id"])
    payment_plan3.unicef_id = "PP-MAN-003"
    payment_plan3.save(update_fields=["unicef_id"])
    url = reverse(
        "api:payments:payment-plans-managerial-list",
        kwargs={"business_area_slug": business_area.slug},
    )
    bulk_url = reverse(
        "api:payments:payment-plans-managerial-bulk-action",
        kwargs={"business_area_slug": business_area.slug},
    )
    return {
        "partner": partner,
        "user": user,
        "client": client,
        "business_area": business_area,
        "program1": program1,
        "program2": program2,
        "payment_plan1": payment_plan1,
        "payment_plan2": payment_plan2,
        "payment_plan3": payment_plan3,
        "url": url,
        "bulk_url": bulk_url,
    }


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([], status.HTTP_403_FORBIDDEN),
        ([Permissions.PAYMENT_VIEW_LIST_MANAGERIAL], status.HTTP_200_OK),
    ],
)
def test_list_payment_plans_permission(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(
        managerial_context["user"],
        permissions,
        managerial_context["business_area"],
        managerial_context["program1"],
    )
    response = managerial_context["client"].get(managerial_context["url"])
    assert response.status_code == expected_status


def test_list_payment_plans(
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
    response_json = response.json()["results"]
    assert len(response_json) == 1
    assert response_json[0]["unicef_id"] == "PP-MAN-001"

    create_partner_role_with_permissions(
        managerial_context["partner"],
        [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
        managerial_context["business_area"],
        program=managerial_context["program2"],
    )

    response = managerial_context["client"].get(managerial_context["url"])
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()["results"]
    assert len(response_json) == 2

    with CaptureQueriesContext(connection) as ctx:
        response = managerial_context["client"].get(managerial_context["url"])
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()["results"]
        assert len(response_json) == 2
        assert "PP-MAN-001" in [
            response_json[0]["unicef_id"],
            response_json[1]["unicef_id"],
        ]
        assert "PP-MAN-002" in [
            response_json[0]["unicef_id"],
            response_json[1]["unicef_id"],
        ]
        assert "PP-MAN-003" not in [
            response_json[0]["unicef_id"],
            response_json[1]["unicef_id"],
        ]
        etag = response.headers["etag"]

        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 8

    with CaptureQueriesContext(connection) as ctx:
        response = managerial_context["client"].get(managerial_context["url"])
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()["results"]
        assert len(response_json) == 2
        etag_second_call = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert etag_second_call == etag
        assert len(ctx.captured_queries) == 8


def test_list_payment_plans_approval_process_data(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    approval_process = ApprovalProcessFactory(
        payment_plan=managerial_context["payment_plan1"],
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
    response = managerial_context["client"].get(managerial_context["url"])
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()["results"]
    assert len(response_json) == 1
    assert response_json[0]["last_approval_process_date"] == approval_process.sent_for_approval_date.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    assert response_json[0]["last_approval_process_by"] == str(approval_process.sent_for_approval_by)

    managerial_context["payment_plan1"].status = PaymentPlan.Status.IN_AUTHORIZATION
    managerial_context["payment_plan1"].save()
    response = managerial_context["client"].get(managerial_context["url"])
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()["results"]
    assert len(response_json) == 1

    assert response_json[0]["last_approval_process_date"] == approval_approval.created_at.strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    assert response_json[0]["last_approval_process_by"] == str(approval_approval.created_by)

    managerial_context["payment_plan1"].status = PaymentPlan.Status.IN_REVIEW
    managerial_context["payment_plan1"].save()
    response = managerial_context["client"].get(managerial_context["url"])
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()["results"]
    assert len(response_json) == 1
    assert response_json[0]["last_approval_process_date"] == approval_authorization.created_at.strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    assert response_json[0]["last_approval_process_by"] == str(approval_authorization.created_by)

    managerial_context["payment_plan1"].status = PaymentPlan.Status.ACCEPTED
    managerial_context["payment_plan1"].save()
    response = managerial_context["client"].get(managerial_context["url"])
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()["results"]
    assert len(response_json) == 1
    assert response_json[0]["last_approval_process_date"] == approval_release.created_at.strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    assert response_json[0]["last_approval_process_by"] == str(approval_release.created_by)


def test_bulk_action(
    managerial_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    create_partner_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        managerial_context["user"],
        [
            Permissions.PM_VIEW_LIST,
            Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
            Permissions.PAYMENT_VIEW_LIST_MANAGERIAL,
        ],
        managerial_context["business_area"],
        managerial_context["program1"],
    )
    create_partner_role_with_permissions(
        managerial_context["partner"],
        [
            Permissions.PM_VIEW_LIST,
            Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
            Permissions.PAYMENT_VIEW_LIST_MANAGERIAL,
        ],
        managerial_context["business_area"],
        managerial_context["program2"],
    )
    ApprovalProcessFactory(payment_plan=managerial_context["payment_plan1"])
    ApprovalProcessFactory(payment_plan=managerial_context["payment_plan2"])
    response = managerial_context["client"].post(
        managerial_context["bulk_url"],
        data={
            "ids": [
                managerial_context["payment_plan1"].id,
                managerial_context["payment_plan2"].id,
            ],
            "action": PaymentPlan.Action.APPROVE.value,
            "comment": "Test comment",
        },
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    managerial_context["payment_plan1"].refresh_from_db()
    managerial_context["payment_plan2"].refresh_from_db()
    assert managerial_context["payment_plan1"].status == PaymentPlan.Status.IN_AUTHORIZATION
    assert managerial_context["payment_plan2"].status == PaymentPlan.Status.IN_AUTHORIZATION


def test_bulk_action_no_approve_permissions(
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
    ApprovalProcessFactory(payment_plan=managerial_context["payment_plan1"])
    ApprovalProcessFactory(payment_plan=managerial_context["payment_plan2"])
    response = managerial_context["client"].post(
        managerial_context["bulk_url"],
        data={
            "ids": [
                managerial_context["payment_plan1"].id,
                managerial_context["payment_plan2"].id,
            ],
            "action": PaymentPlan.Action.APPROVE.value,
            "comment": "Test comment",
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    managerial_context["payment_plan1"].refresh_from_db()
    managerial_context["payment_plan2"].refresh_from_db()
    assert managerial_context["payment_plan1"].status == PaymentPlan.Status.IN_APPROVAL
    assert managerial_context["payment_plan2"].status == PaymentPlan.Status.IN_APPROVAL


@pytest.mark.parametrize(
    ("action_name", "result"),
    [
        (PaymentPlan.Action.APPROVE.name, Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.name),
        (PaymentPlan.Action.AUTHORIZE.name, Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE.name),
        (PaymentPlan.Action.REVIEW.name, Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW.name),
        ("Some other action name", None),
    ],
)
def test_get_action_permission(action_name: str, result: str | None) -> None:
    payment_plan_managerial_viewset = PaymentPlanManagerialViewSet()
    assert payment_plan_managerial_viewset._get_action_permission(action_name) == result
