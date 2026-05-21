from decimal import Decimal
from tempfile import NamedTemporaryFile
from types import SimpleNamespace
from urllib.parse import urlparse

import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.payment.celery_tasks import (
    create_follow_up_instruction_delivery_xlsx_async_task_action,
    import_follow_up_instruction_reconciliation_from_xlsx_async_task_action,
)
from hope.apps.payment.xlsx.xlsx_follow_up_instruction_delivery_export_service import (
    XlsxFollowUpInstructionDeliveryExportService,
)
from hope.models import BusinessArea, FollowUpInstruction, PaymentPlanGroup, Program, User

pytestmark = pytest.mark.django_db()


def _select_autocomplete_option(browser: HopeTestBrowser, label: str) -> None:
    browser.type('input[aria-label="Payment Plan Groups"]', label)
    browser.wait_for_element_visible('li[role="option"]')
    browser.click('li[role="option"]')


def _confirm_workflow_button(browser: HopeTestBrowser, button_cy: str) -> None:
    browser.wait_for_element_clickable(f'[data-cy="{button_cy}"]')
    browser.click(f'[data-cy="{button_cy}"]')
    browser.wait_for_element_clickable(f'[data-cy="{button_cy}-confirm"]')
    browser.click(f'[data-cy="{button_cy}-confirm"]')


def _build_xlsx_with_deliveries(instruction: FollowUpInstruction, deliveries: list[Decimal | None]) -> str:
    """Build reconciliation XLSX with per-row delivered_quantity values. Returns temp file path.

    deliveries[0] → row 2 (first data row), deliveries[1] → row 3, etc.
    Pass None to leave a cell empty.
    """
    wb = XlsxFollowUpInstructionDeliveryExportService(instruction).generate_workbook()
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    delivered_col = headers.index("delivered_quantity") + 1
    for i, qty in enumerate(deliveries, start=2):
        ws.cell(row=i, column=delivered_col).value = qty
    with NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        wb.save(tmp.name)
        return tmp.name


def _drive_to_accepted(
    login: HopeTestBrowser,
    base_url: str,
    group_one: PaymentPlanGroup,
    group_two: PaymentPlanGroup,
) -> str:
    """Drive a new Follow-up Instruction through the full approval workflow to Accepted.

    Creates the instruction via the UI, runs through all workflow steps, and returns
    the detail page path (e.g. '/.../follow-up-instructions/<id>').
    """
    login.open(f"{base_url}/payment-module/follow-up-instructions")
    login.wait_for_text("Follow-up Instructions")

    login.wait_for_element_clickable('[data-cy="button-create-follow-up-instruction"]')
    login.click('[data-cy="button-create-follow-up-instruction"]')
    login.wait_for_element_visible('input[aria-label="Payment Plan Groups"]')

    _select_autocomplete_option(login, group_one.unicef_id or group_one.name)
    _select_autocomplete_option(login, group_two.unicef_id or group_two.name)

    login.type('input[name="dispersionStartDate"]', "01/01/2027")
    login.type('input[name="dispersionEndDate"]', "12/31/2027")
    login.click('[data-cy="button-submit-create-follow-up-instruction"]')

    login.wait_for_text("Open")
    login.wait_for_element_visible('[data-cy="button-lock"]')
    login.assert_element_absent('[data-cy="button-lock-fsp"]')
    login.assert_element_absent('[data-cy="button-send-for-approval"]')

    detail_path = urlparse(login.get_current_url()).path

    login.click('[data-cy="button-lock"]')
    login.wait_for_text("Locked")
    login.wait_for_element_absent('[data-cy="button-lock"]')
    login.wait_for_element_visible('[data-cy="button-unlock"]')
    login.wait_for_element_visible('[data-cy="button-lock-fsp"]')
    login.wait_for_element_visible('[data-cy="button-abort"]')

    login.click('[data-cy="button-lock-fsp"]')
    login.wait_for_text("Locked FSP")
    login.wait_for_element_absent('[data-cy="button-lock-fsp"]')
    login.wait_for_element_absent('[data-cy="button-unlock"]')
    login.wait_for_element_visible('[data-cy="button-unlock-fsp"]')
    login.wait_for_element_visible('[data-cy="button-send-for-approval"]')
    login.wait_for_element_visible('[data-cy="button-abort"]')

    login.click('[data-cy="button-send-for-approval"]')
    login.wait_for_text("In Approval")
    login.wait_for_element_absent('[data-cy="button-send-for-approval"]')
    login.wait_for_element_visible('[data-cy="button-approve"]')
    login.wait_for_element_visible('[data-cy="button-reject"]')
    login.wait_for_element_visible('[data-cy="button-abort"]')

    _confirm_workflow_button(login, "button-approve")
    login.wait_for_text("In Authorization")
    login.wait_for_element_absent('[data-cy="button-approve"]')
    login.wait_for_element_visible('[data-cy="button-authorize"]')
    login.wait_for_element_visible('[data-cy="button-reject"]')
    login.wait_for_element_visible('[data-cy="button-abort"]')

    _confirm_workflow_button(login, "button-authorize")
    login.wait_for_text("In Review")
    login.wait_for_element_absent('[data-cy="button-authorize"]')
    login.wait_for_element_visible('[data-cy="button-mark-as-released"]')
    login.wait_for_element_visible('[data-cy="button-reject"]')
    login.wait_for_element_visible('[data-cy="button-abort"]')

    _confirm_workflow_button(login, "button-mark-as-released")
    login.wait_for_text("Accepted")
    login.wait_for_element_visible('[data-cy="button-reconciliation-export"]')
    login.wait_for_element_visible('[data-cy="button-reconciliation-import"]')
    login.wait_for_element_absent('[data-cy="button-mark-as-released"]')
    login.assert_element_absent('[data-cy="button-close"]')

    return detail_path


def _upload_reconciliation_xlsx(browser: HopeTestBrowser, file_path: str) -> None:
    """Upload reconciliation XLSX via the dialog and wait for confirmation."""
    browser.click('[data-cy="button-reconciliation-import"]')
    browser.wait_for_element_visible('[data-cy="dialog-reconciliation-import"]')
    browser.choose_file('input[type="file"]', file_path)
    browser.wait_for_element_clickable('[data-cy="button-reconciliation-import-submit"]')
    browser.click('[data-cy="button-reconciliation-import-submit"]')
    browser.wait_for_text("Reconciliation import started")


def _run_export_task(instruction_id: str) -> None:
    """Execute the XLSX export Celery task synchronously."""
    superuser = User.objects.get(username="superuser")
    job = SimpleNamespace(config={"follow_up_instruction_id": instruction_id, "user_id": str(superuser.pk)})
    create_follow_up_instruction_delivery_xlsx_async_task_action(job)


def _run_reconciliation_import_task(instruction_id: str) -> None:
    """Execute the reconciliation import Celery task synchronously."""
    job = SimpleNamespace(config={"follow_up_instruction_id": instruction_id})
    import_follow_up_instruction_reconciliation_from_xlsx_async_task_action(job)


def _create_instruction_via_ui(
    login: HopeTestBrowser,
    base_url: str,
    group_one: PaymentPlanGroup,
    group_two: PaymentPlanGroup,
) -> str:
    """Create a Follow-up Instruction via UI and return the detail path at Open state."""
    login.open(f"{base_url}/payment-module/follow-up-instructions")
    login.wait_for_text("Follow-up Instructions")
    login.wait_for_element_clickable('[data-cy="button-create-follow-up-instruction"]')
    login.click('[data-cy="button-create-follow-up-instruction"]')
    login.wait_for_element_visible('input[aria-label="Payment Plan Groups"]')
    _select_autocomplete_option(login, group_one.unicef_id or group_one.name)
    _select_autocomplete_option(login, group_two.unicef_id or group_two.name)
    login.type('input[name="dispersionStartDate"]', "01/01/2027")
    login.type('input[name="dispersionEndDate"]', "12/31/2027")
    login.click('[data-cy="button-submit-create-follow-up-instruction"]')
    login.wait_for_text("Open")
    return urlparse(login.get_current_url()).path


def test_follow_up_instruction_full_flow(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    fi_program: Program,
    fi_source_plans: tuple[PaymentPlanGroup, PaymentPlanGroup],
) -> None:
    group_one, group_two = fi_source_plans
    ba_slug = business_area.slug
    program_code = fi_program.code
    base_url = f"/{ba_slug}/programs/{program_code}"

    # Drive through the full approval workflow to Accepted
    detail_path = _drive_to_accepted(login, base_url, group_one, group_two)
    instruction_id = detail_path.rstrip("/").rsplit("/", 1)[-1]

    # Both child plans mirror the Accepted status; no reconciliation has happened yet
    login.wait_for_text("Accepted", '[data-cy="plan-status-0"]')
    login.wait_for_text("Accepted", '[data-cy="plan-status-1"]')
    login.wait_for_text("280.00", '[data-cy="summary-total-entitled"]')
    login.wait_for_text("0.00", '[data-cy="summary-total-delivered"]')

    # --- Export XLSX ---
    login.click('[data-cy="button-reconciliation-export"]')
    login.wait_for_text("Exporting XLSX started")
    _run_export_task(instruction_id)
    login.open(detail_path)
    login.wait_for_element_visible('[data-cy="button-download-export"]')

    # --- Partial reconciliation: hh_a=140 (full), hh_b=30 (partial), hh_c=0 (undelivered) ---
    instruction = FollowUpInstruction.objects.get(pk=instruction_id)
    partial_path = _build_xlsx_with_deliveries(
        instruction,
        [Decimal("140.00"), Decimal("30.00"), Decimal("0.00")],
    )
    _upload_reconciliation_xlsx(login, partial_path)
    _run_reconciliation_import_task(instruction_id)

    login.open(detail_path)
    # hh_b is DISTRIBUTION_PARTIAL (30/60 delivered) → plan_one stays Accepted
    # hh_c is NOT_DISTRIBUTED (0/80) and hh_a is fully delivered → plan_two transitions to Finished
    login.wait_for_text("Accepted")
    login.wait_for_text("Accepted", '[data-cy="plan-status-0"]')
    login.wait_for_text("Finished", '[data-cy="plan-status-1"]')
    # plan_one: delivered = hh_a(100) + hh_b(30) = 130; undelivered = 30
    login.wait_for_text("130.00", '[data-cy="plan-delivered-0"]')
    login.wait_for_text("30.00", '[data-cy="plan-undelivered-0"]')
    # plan_two: delivered = hh_a(40) + hh_c(0) = 40; undelivered = 80
    login.wait_for_text("40.00", '[data-cy="plan-delivered-1"]')
    login.wait_for_text("80.00", '[data-cy="plan-undelivered-1"]')
    # Instruction totals: delivered=170, undelivered=110
    login.wait_for_text("170.00", '[data-cy="summary-total-delivered"]')
    login.wait_for_text("110.00", '[data-cy="summary-total-undelivered"]')
    login.assert_element_absent('[data-cy="button-close"]')

    # --- Re-export after partial reconciliation ---
    login.click('[data-cy="button-reconciliation-export"]')
    login.wait_for_text("Exporting XLSX started")
    _run_export_task(instruction_id)
    login.open(detail_path)
    login.wait_for_element_visible('[data-cy="button-download-export"]')

    # --- Full reconciliation: hh_a=140, hh_b=60 (remaining), hh_c=80 ---
    instruction.refresh_from_db()
    full_path = _build_xlsx_with_deliveries(
        instruction,
        [Decimal("140.00"), Decimal("60.00"), Decimal("80.00")],
    )
    _upload_reconciliation_xlsx(login, full_path)
    _run_reconciliation_import_task(instruction_id)

    login.open(detail_path)
    # All payments fully delivered — instruction and both child plans transition to Finished
    login.wait_for_text("Finished")
    login.wait_for_text("Finished", '[data-cy="plan-status-0"]')
    login.wait_for_text("Finished", '[data-cy="plan-status-1"]')
    # plan_one: fully delivered 160/160; plan_two: fully delivered 120/120
    login.wait_for_text("160.00", '[data-cy="plan-delivered-0"]')
    login.wait_for_text("120.00", '[data-cy="plan-delivered-1"]')
    # Instruction summary: all 280 delivered, 0 undelivered
    login.wait_for_text("280.00", '[data-cy="summary-total-delivered"]')
    login.wait_for_text("0.00", '[data-cy="summary-total-undelivered"]')
    login.wait_for_element_visible('[data-cy="button-reconciliation-export"]')
    login.wait_for_element_visible('[data-cy="button-reconciliation-import"]')
    login.wait_for_element_visible('[data-cy="button-close"]')
    login.assert_element_absent('[data-cy="button-mark-as-released"]')

    # --- Close ---
    login.click('[data-cy="button-close"]')
    login.wait_for_text("Follow-up Instruction closed")
    login.wait_for_text("Closed")
    login.assert_element_absent('[data-cy="button-close"]')
    login.assert_element_absent('[data-cy="button-reconciliation-export"]')
    login.assert_element_absent('[data-cy="button-reconciliation-import"]')


def test_detail_page_totals_at_open(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    fi_program: Program,
    fi_instruction: FollowUpInstruction,
) -> None:
    """Detail page shows correct aggregate totals and child-plan statuses right after creation."""
    ba_slug = business_area.slug
    program_code = fi_program.code
    detail_path = f"/{ba_slug}/programs/{program_code}/payment-module/follow-up-instructions/{fi_instruction.pk}"

    login.open(detail_path)

    # Instruction status
    login.wait_for_text("Open")

    # Summary: hh_a(100+40=140) + hh_b(60) + hh_c(80) = 280 AFN entitled, none delivered yet
    login.wait_for_text("280.00", '[data-cy="summary-total-entitled"]')
    login.wait_for_text("0.00", '[data-cy="summary-total-delivered"]')
    login.wait_for_text("280.00", '[data-cy="summary-total-undelivered"]')
    login.wait_for_text("3", '[data-cy="summary-households-count"]')
    login.wait_for_text("2", '[data-cy="summary-child-plans-count"]')

    # Child plans table: both plans Open with correct per-plan entitlements and zero delivery
    login.wait_for_text("Open", '[data-cy="plan-status-0"]')
    login.wait_for_text("Open", '[data-cy="plan-status-1"]')
    # plan_one (group_one): hh_a=100 + hh_b=60 → entitled=160
    login.wait_for_text("160.00", '[data-cy="plan-entitled-0"]')
    login.wait_for_text("0.00", '[data-cy="plan-delivered-0"]')
    # plan_two (group_two): hh_a=40 + hh_c=80 → entitled=120
    login.wait_for_text("120.00", '[data-cy="plan-entitled-1"]')
    login.wait_for_text("0.00", '[data-cy="plan-delivered-1"]')

    # Workflow buttons: Lock available; reconciliation/close not yet accessible
    login.wait_for_element_visible('[data-cy="button-lock"]')
    login.assert_element_absent('[data-cy="button-reconciliation-export"]')
    login.assert_element_absent('[data-cy="button-close"]')


def test_reconciliation_full_undelivered(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    fi_program: Program,
    fi_source_plans: tuple[PaymentPlanGroup, PaymentPlanGroup],
) -> None:
    """All-zero reconciliation closes out every payment as undelivered and transitions to Finished."""
    group_one, group_two = fi_source_plans
    ba_slug = business_area.slug
    program_code = fi_program.code
    base_url = f"/{ba_slug}/programs/{program_code}"

    detail_path = _drive_to_accepted(login, base_url, group_one, group_two)
    instruction_id = detail_path.rstrip("/").rsplit("/", 1)[-1]

    instruction = FollowUpInstruction.objects.get(pk=instruction_id)
    zero_path = _build_xlsx_with_deliveries(
        instruction,
        [Decimal("0.00"), Decimal("0.00"), Decimal("0.00")],
    )
    _upload_reconciliation_xlsx(login, zero_path)
    _run_reconciliation_import_task(instruction_id)

    login.open(detail_path)
    # All payments NOT_DISTRIBUTED → all plans Finished → instruction Finished
    login.wait_for_text("Finished")
    login.wait_for_text("Finished", '[data-cy="plan-status-0"]')
    login.wait_for_text("Finished", '[data-cy="plan-status-1"]')
    login.wait_for_text("280.00", '[data-cy="summary-total-entitled"]')
    login.wait_for_text("0.00", '[data-cy="summary-total-delivered"]')
    login.wait_for_text("280.00", '[data-cy="summary-total-undelivered"]')
    login.wait_for_element_visible('[data-cy="button-close"]')


def test_child_plan_statuses_at_accepted(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    fi_program: Program,
    fi_source_plans: tuple[PaymentPlanGroup, PaymentPlanGroup],
) -> None:
    """Child plans table mirrors Accepted status; per-plan entitlements match source data before reconciliation."""
    group_one, group_two = fi_source_plans
    base_url = f"/{business_area.slug}/programs/{fi_program.code}"
    detail_path = _drive_to_accepted(login, base_url, group_one, group_two)
    login.open(detail_path)

    login.wait_for_text("Accepted", '[data-cy="plan-status-0"]')
    login.wait_for_text("Accepted", '[data-cy="plan-status-1"]')
    # plan_one: hh_a(100) + hh_b(60) = 160 entitled, 0 delivered
    login.wait_for_text("160.00", '[data-cy="plan-entitled-0"]')
    login.wait_for_text("0.00", '[data-cy="plan-delivered-0"]')
    # plan_two: hh_a(40) + hh_c(80) = 120 entitled, 0 delivered
    login.wait_for_text("120.00", '[data-cy="plan-entitled-1"]')
    login.wait_for_text("0.00", '[data-cy="plan-delivered-1"]')
    # Instruction summary: 280 entitled, 0 delivered, 280 undelivered (no reconciliation yet)
    login.wait_for_text("280.00", '[data-cy="summary-total-entitled"]')
    login.wait_for_text("0.00", '[data-cy="summary-total-delivered"]')
    login.wait_for_text("280.00", '[data-cy="summary-total-undelivered"]')


def test_abort_from_locked(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    fi_program: Program,
    fi_source_plans: tuple[PaymentPlanGroup, PaymentPlanGroup],
) -> None:
    """Instruction aborted from Locked shows Aborted status and Reactivate button."""
    group_one, group_two = fi_source_plans
    base_url = f"/{business_area.slug}/programs/{fi_program.code}"
    _create_instruction_via_ui(login, base_url, group_one, group_two)

    login.click('[data-cy="button-lock"]')
    login.wait_for_text("Locked")

    _confirm_workflow_button(login, "button-abort")
    login.wait_for_text("Aborted")
    login.assert_element_absent('[data-cy="button-abort"]')
    login.assert_element_absent('[data-cy="button-lock"]')
    login.wait_for_element_visible('[data-cy="button-reactivate"]')


def test_reject_from_in_approval_reverts_to_locked_fsp(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    fi_program: Program,
    fi_source_plans: tuple[PaymentPlanGroup, PaymentPlanGroup],
) -> None:
    """Rejecting from In Approval sends the instruction back to Locked FSP."""
    group_one, group_two = fi_source_plans
    base_url = f"/{business_area.slug}/programs/{fi_program.code}"
    _create_instruction_via_ui(login, base_url, group_one, group_two)

    login.click('[data-cy="button-lock"]')
    login.wait_for_text("Locked")
    login.click('[data-cy="button-lock-fsp"]')
    login.wait_for_text("Locked FSP")
    login.click('[data-cy="button-send-for-approval"]')
    login.wait_for_text("In Approval")

    _confirm_workflow_button(login, "button-reject")
    login.wait_for_text("Locked FSP")
    login.wait_for_element_visible('[data-cy="button-unlock-fsp"]')
    login.wait_for_element_absent('[data-cy="button-approve"]')
    login.assert_element_absent('[data-cy="button-close"]')
