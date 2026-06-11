from decimal import Decimal
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
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FollowUpInstructionFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import FollowUpInstruction, Payment, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def delivery_mechanism() -> Any:
    return DeliveryMechanismFactory(code="cash", name="Cash", payment_gateway_id="dm-cash")


@pytest.fixture
def fsp(delivery_mechanism: Any) -> Any:
    fsp = FinancialServiceProviderFactory()
    fsp.delivery_mechanisms.add(delivery_mechanism)
    return fsp


@pytest.fixture
def delivery_template(fsp: Any, delivery_mechanism: Any) -> Any:
    template = FinancialServiceProviderXlsxTemplateFactory(
        columns=["payment_id", "entitlement_quantity", "delivered_quantity"],
        core_fields=[],
        flex_fields=[],
        document_types=[],
    )
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        xlsx_template=template,
    )
    return template


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


def test_create_follow_up_instruction(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(ctx["user"], [Permissions.PM_CREATE], ctx["business_area"], ctx["program"])
    group = PaymentPlanGroupFactory(cycle=ctx["cycle"])
    source_plan = PaymentPlanFactory(
        program_cycle=ctx["cycle"],
        payment_plan_group=group,
        business_area=ctx["business_area"],
        currency=ctx["currency"],
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        status=PaymentPlan.Status.FINISHED,
    )
    PaymentFactory(
        parent=source_plan,
        program=source_plan.program,
        currency=ctx["currency"],
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("100.00"),
        status=Payment.STATUS_ERROR,
    )
    url = reverse(
        "api:payments:follow-up-instructions-list",
        kwargs={"business_area_slug": ctx["business_area"].slug, "program_code": ctx["program"].code},
    )

    response = ctx["client"].post(
        url,
        {
            "dispersion_start_date": "2026-07-01",
            "dispersion_end_date": "2026-09-30",
            "payment_plan_group_ids": [str(group.pk)],
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    created = FollowUpInstruction.objects.get(id=response.json()["id"])
    assert created.payment_plans.count() == 1
    assert created.payment_plans.first().source_payment_plan_id == source_plan.id


def test_follow_up_instruction_lock(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_LOCK_AND_UNLOCK], ctx["business_area"], ctx["program"]
    )
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    PaymentFactory(
        parent=pp,
        program=pp.program,
        currency=ctx["currency"],
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("100.00"),
        status=Payment.STATUS_PENDING,
    )
    url = reverse(
        "api:payments:follow-up-instructions-lock",
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


def test_follow_up_instruction_lock_fsp(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_LOCK_AND_UNLOCK_FSP], ctx["business_area"], ctx["program"]
    )
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    PaymentFactory(
        parent=pp,
        program=pp.program,
        currency=ctx["currency"],
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("100.00"),
        status=Payment.STATUS_PENDING,
    )
    url = reverse(
        "api:payments:follow-up-instructions-lock-fsp",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].get(url)

    assert response.status_code == status.HTTP_200_OK
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.LOCKED_FSP


def test_follow_up_instruction_send_for_approval(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_SEND_FOR_APPROVAL], ctx["business_area"], ctx["program"]
    )
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED_FSP,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    url = reverse(
        "api:payments:follow-up-instructions-send-for-approval",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].get(url)

    assert response.status_code == status.HTTP_200_OK
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.IN_APPROVAL


def test_follow_up_instruction_approve(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE], ctx["business_area"], ctx["program"]
    )
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.IN_APPROVAL,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
    )
    ApprovalProcessFactory(payment_plan=pp)
    url = reverse(
        "api:payments:follow-up-instructions-approve",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].post(url, {"comment": "approved"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.IN_AUTHORIZATION


def test_follow_up_instruction_authorize(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE], ctx["business_area"], ctx["program"]
    )
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.IN_AUTHORIZATION,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
    )
    ApprovalProcessFactory(payment_plan=pp)
    url = reverse(
        "api:payments:follow-up-instructions-authorize",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].post(url, {"comment": "authorized"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.IN_REVIEW


def test_follow_up_instruction_mark_as_released(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW], ctx["business_area"], ctx["program"]
    )
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.IN_REVIEW,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
    )
    ApprovalProcessFactory(payment_plan=pp)
    url = reverse(
        "api:payments:follow-up-instructions-mark-as-released",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].post(url, {"comment": "released"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.ACCEPTED


def test_follow_up_instruction_delivery_export_xlsx(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    delivery_mechanism: Any,
    fsp: Any,
    delivery_template: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(ctx["user"], [Permissions.PM_VIEW_LIST], ctx["business_area"], ctx["program"])
    PaymentFactory(
        parent=PaymentPlanFactory(
            status=PaymentPlan.Status.ACCEPTED,
            follow_up_instruction=ctx["instruction"],
            program_cycle=ctx["cycle"],
            currency=ctx["currency"],
            delivery_mechanism=delivery_mechanism,
            financial_service_provider=fsp,
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        ),
        program=ctx["program"],
        currency=ctx["currency"],
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("100.00"),
        status=Payment.STATUS_PENDING,
    )
    url = reverse(
        "api:payments:follow-up-instructions-delivery-export-xlsx",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].get(url)

    assert response.status_code == status.HTTP_200_OK
    instruction = ctx["instruction"]
    instruction.refresh_from_db()
    assert instruction.background_action_status == FollowUpInstruction.BackgroundActionStatus.XLSX_EXPORTING


def test_follow_up_instruction_delivery_import_xlsx(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION], ctx["business_area"], ctx["program"]
    )
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        exchange_rate=Decimal("1.00"),
    )
    payment = PaymentFactory(
        parent=pp,
        program=pp.program,
        currency=ctx["currency"],
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("100.00"),
        delivered_quantity=Decimal("0.00"),
        status=Payment.STATUS_PENDING,
    )
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["household_id", "delivered_quantity"])
    ws.append([payment.household.unicef_id, "100.00"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    xlsx_file = SimpleUploadedFile("reconciliation.xlsx", buf.read(), content_type="application/vnd.ms-excel")
    url = reverse(
        "api:payments:follow-up-instructions-delivery-import-xlsx",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].post(url, {"file": xlsx_file}, format="multipart")

    assert response.status_code == status.HTTP_200_OK
    instruction = ctx["instruction"]
    instruction.refresh_from_db()
    assert (
        instruction.background_action_status == FollowUpInstruction.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION
    )
    assert instruction.reconciliation_import_file is not None


def test_follow_up_instruction_close(
    follow_up_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    delivery_mechanism: Any,
    fsp: Any,
) -> None:
    ctx = follow_up_context
    create_user_role_with_permissions(
        ctx["user"], [Permissions.PM_CLOSE_FINISHED], ctx["business_area"], ctx["program"]
    )
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.FINISHED,
        follow_up_instruction=ctx["instruction"],
        program_cycle=ctx["cycle"],
        currency=ctx["currency"],
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    url = reverse(
        "api:payments:follow-up-instructions-close",
        kwargs={
            "business_area_slug": ctx["business_area"].slug,
            "program_code": ctx["program"].code,
            "pk": ctx["instruction"].pk,
        },
    )

    response = ctx["client"].get(url)

    assert response.status_code == status.HTTP_200_OK
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.CLOSED
