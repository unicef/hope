import io
from typing import Any, Callable

from django.core.files.uploadedfile import SimpleUploadedFile
import openpyxl
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    ApprovalProcessFactory,
    BusinessAreaFactory,
    CurrencyFactory,
    FollowUpInstructionFactory,
    PartnerFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import FollowUpInstruction, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def follow_up_context(api_client: Callable, business_area: Any) -> dict[str, Any]:
    partner = PartnerFactory()
    user = UserFactory(partner=partner)
    program = ProgramFactory(business_area=business_area)
    client = api_client(user)
    cycle = ProgramCycleFactory(program=program)
    currency = CurrencyFactory(code="USD")
    instruction = FollowUpInstructionFactory(program=program, business_area=business_area, created_by=user)
    return {
        "business_area": business_area,
        "user": user,
        "client": client,
        "program": program,
        "cycle": cycle,
        "currency": currency,
        "instruction": instruction,
    }


def test_follow_up_instruction_detail_is_scoped_to_program(
    api_client: Callable,
    create_user_role_with_permissions: Any,
    business_area: Any,
) -> None:
    partner = PartnerFactory(name="Test Partner")
    user = UserFactory(partner=partner)
    client = api_client(user)
    program_with_access = ProgramFactory(business_area=business_area)
    other_program = ProgramFactory(business_area=business_area)
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=other_program,
        created_by=user,
    )

    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_DETAILS],
        business_area,
        program_with_access,
    )

    url = reverse(
        "api:payments:follow-up-instructions-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program_with_access.code,
            "pk": instruction.pk,
        },
    )
    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_follow_up_instruction_rejects_duplicate_group_ids(
    api_client: Callable,
    create_user_role_with_permissions: Any,
    business_area: Any,
) -> None:
    partner = PartnerFactory(name="TestPartnerFI")
    user = UserFactory(partner=partner)
    program = ProgramFactory(business_area=business_area)
    create_user_role_with_permissions(user, [Permissions.PM_CREATE], business_area, program)
    client = api_client(user)
    cycle = ProgramCycleFactory(program=program)
    group = PaymentPlanGroupFactory(cycle=cycle)
    duplicate_id = str(group.pk)
    url = reverse(
        "api:payments:follow-up-instructions-list",
        kwargs={"business_area_slug": business_area.slug, "program_code": program.code},
    )

    response = client.post(
        url,
        {
            "dispersion_start_date": "2025-01-01",
            "dispersion_end_date": "2025-03-31",
            "payment_plan_group_ids": [duplicate_id, duplicate_id],
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Duplicate Payment Plan Group IDs are not allowed." in str(response.json()["payment_plan_group_ids"])


def test_follow_up_instruction_unlock(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_LOCK_AND_UNLOCK], ctx["business_area"], ctx["program"]
    )
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
    )
    url = reverse(
        "api:payments:follow-up-instructions-unlock",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].get(url)

    assert response.status_code == status.HTTP_200_OK
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.OPEN


def test_follow_up_instruction_unlock_fsp(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_LOCK_AND_UNLOCK_FSP], ctx["business_area"], ctx["program"]
    )
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED_FSP,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
    )
    url = reverse(
        "api:payments:follow-up-instructions-unlock-fsp",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].get(url)

    assert response.status_code == status.HTTP_200_OK
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.LOCKED


def test_follow_up_instruction_reject(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(ctx["user"], [Permissions.PM_VIEW_LIST], ctx["business_area"], ctx["program"])
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.IN_APPROVAL,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
    )
    ApprovalProcessFactory(payment_plan=pp)
    url = reverse(
        "api:payments:follow-up-instructions-reject",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].post(url, {"comment": "rejected"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.LOCKED_FSP


def test_follow_up_instruction_delivery_import_xlsx_missing_file(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION], ctx["business_area"], ctx["program"]
    )
    url = reverse(
        "api:payments:follow-up-instructions-delivery-import-xlsx",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].post(url, {}, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "file" in response.json()


def test_follow_up_instruction_delivery_import_xlsx_bad_zip_file(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION], ctx["business_area"], ctx["program"]
    )
    url = reverse(
        "api:payments:follow-up-instructions-delivery-import-xlsx",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )
    bad_file = SimpleUploadedFile("reconciliation.xlsx", b"not-a-zip-file", content_type="application/vnd.ms-excel")

    response = ctx["client"].post(url, {"file": bad_file}, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Wrong file type or password protected" in response.data[0]


def test_follow_up_instruction_delivery_import_xlsx_returns_400_on_errors(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION], ctx["business_area"], ctx["program"]
    )
    url = reverse(
        "api:payments:follow-up-instructions-delivery-import-xlsx",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["wrong_col_a", "wrong_col_b"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    xlsx_file = SimpleUploadedFile("reconciliation.xlsx", buf.read(), content_type="application/vnd.ms-excel")

    response = ctx["client"].post(url, {"file": xlsx_file}, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_follow_up_instruction_abort(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(ctx["user"], [Permissions.PM_ABORT], ctx["business_area"], ctx["program"])
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
    )
    url = reverse(
        "api:payments:follow-up-instructions-abort",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].post(url, {"abort_comment": "stopping"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.ABORTED


def test_follow_up_instruction_reactivate_abort(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_REACTIVATE_ABORT], ctx["business_area"], ctx["program"]
    )
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.ABORTED,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
    )
    url = reverse(
        "api:payments:follow-up-instructions-reactivate-abort",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].get(url)

    assert response.status_code == status.HTTP_200_OK
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.OPEN
