from decimal import Decimal
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.payment.xlsx.xlsx_follow_up_instruction_delivery_export_service import (
    XlsxFollowUpInstructionDeliveryExportService,
)
from hope.models import BusinessArea, FollowUpInstruction, PaymentPlanGroup, Program

pytestmark = pytest.mark.django_db()


def _select_autocomplete_option(browser: HopeTestBrowser, label: str) -> None:
    # Append with send_keys; browser.type() clears the field first, which on a
    # MUI multi-autocomplete backspaces away an already-selected chip.
    el = browser.find_element('input[aria-label="Payment Plan Groups"]')
    el.send_keys(label)
    browser.wait_for_element_visible('li[role="option"]')
    browser.click('li[role="option"]')


def _fill_date(browser: HopeTestBrowser, name: str, value: str) -> None:
    browser.fill_date(f'input[name="{name}"]', value)


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


def _upload_reconciliation_xlsx(browser: HopeTestBrowser, file_path: str) -> None:
    """Upload reconciliation XLSX via the dialog and wait for confirmation."""
    browser.click('[data-cy="button-reconciliation-import"]')
    browser.wait_for_element_visible('[data-cy="dialog-reconciliation-import"]')
    browser.choose_file('input[type="file"]', file_path)
    browser.wait_for_element_clickable('[data-cy="button-reconciliation-import-submit"]')
    browser.click('[data-cy="button-reconciliation-import-submit"]')
    browser.wait_for_text("Reconciliation import started")


def test_follow_up_instruction_full_flow(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    fi_program: Program,
    fi_source_plans: tuple[PaymentPlanGroup, PaymentPlanGroup],
) -> None:
    group_one, group_two = fi_source_plans
    base_url = f"/{business_area.slug}/programs/{fi_program.code}"

    # --- Create instruction via UI ---
    login.open(f"{base_url}/payment-module/follow-up-instructions")
    login.wait_for_text("Follow-up Instructions")
    login.wait_for_element_clickable('[data-cy="button-create-follow-up-instruction"]')
    login.click('[data-cy="button-create-follow-up-instruction"]')
    login.wait_for_element_visible('input[aria-label="Payment Plan Groups"]')
    _select_autocomplete_option(login, group_one.unicef_id or group_one.name)
    _select_autocomplete_option(login, group_two.unicef_id or group_two.name)
    _fill_date(login, "dispersionStartDate", "2027-01-01")
    _fill_date(login, "dispersionEndDate", "2027-12-31")
    login.click('[data-cy="button-submit-create-follow-up-instruction"]')

    # --- Open state: verify totals, counts, and per-plan statuses ---
    login.wait_for_text("OPEN")
    login.wait_for_element_visible('[data-cy="button-lock"]')
    login.assert_element_absent('[data-cy="button-lock-fsp"]')
    login.assert_element_absent('[data-cy="button-send-for-approval"]')
    # Summary: hh_a(100+40=140) + hh_b(60) + hh_c(80) = 280 USD entitled, none delivered yet
    login.wait_for_text("280.00", '[data-cy="summary-total-entitled"]')
    login.wait_for_text("0.00", '[data-cy="summary-total-delivered"]')
    login.wait_for_text("280.00", '[data-cy="summary-total-undelivered"]')
    login.wait_for_text("3", '[data-cy="summary-households-count"]')
    login.wait_for_text("2", '[data-cy="summary-child-plans-count"]')
    # Both child plans are Open with correct per-plan entitlements
    login.wait_for_text("OPEN", '[data-cy="plan-status-0"]')
    login.wait_for_text("OPEN", '[data-cy="plan-status-1"]')
    login.wait_for_text("160.00", '[data-cy="plan-entitled-0"]')  # hh_a(100) + hh_b(60)
    login.wait_for_text("0.00", '[data-cy="plan-delivered-0"]')
    login.wait_for_text("120.00", '[data-cy="plan-entitled-1"]')  # hh_a(40) + hh_c(80)
    login.wait_for_text("0.00", '[data-cy="plan-delivered-1"]')
    login.assert_element_absent('[data-cy="button-reconciliation-export"]')
    login.assert_element_absent('[data-cy="button-close"]')

    detail_path = urlparse(login.get_current_url()).path
    instruction_id = detail_path.rstrip("/").rsplit("/", 1)[-1]

    # --- Lock ---
    login.click('[data-cy="button-lock"]')
    login.wait_for_text("LOCKED")
    login.wait_for_element_absent('[data-cy="button-lock"]')
    login.wait_for_element_visible('[data-cy="button-unlock"]')
    login.wait_for_element_visible('[data-cy="button-lock-fsp"]')
    login.wait_for_element_visible('[data-cy="button-abort"]')

    # --- Lock FSP ---
    login.click('[data-cy="button-lock-fsp"]')
    login.wait_for_text("LOCKED FSP")
    login.wait_for_element_absent('[data-cy="button-lock-fsp"]')
    login.wait_for_element_absent('[data-cy="button-unlock"]')
    login.wait_for_element_visible('[data-cy="button-unlock-fsp"]')
    login.wait_for_element_visible('[data-cy="button-send-for-approval"]')
    login.wait_for_element_visible('[data-cy="button-abort"]')

    # --- Send for approval ---
    login.click('[data-cy="button-send-for-approval"]')
    login.wait_for_text("IN APPROVAL")
    login.wait_for_element_absent('[data-cy="button-send-for-approval"]')
    login.wait_for_element_visible('[data-cy="button-approve"]')
    login.wait_for_element_visible('[data-cy="button-reject"]')
    login.wait_for_element_visible('[data-cy="button-abort"]')

    # --- Approve ---
    _confirm_workflow_button(login, "button-approve")
    login.wait_for_text("IN AUTHORIZATION")
    login.wait_for_element_absent('[data-cy="button-approve"]')
    login.wait_for_element_visible('[data-cy="button-authorize"]')
    login.wait_for_element_visible('[data-cy="button-reject"]')
    login.wait_for_element_visible('[data-cy="button-abort"]')

    # --- Authorize ---
    _confirm_workflow_button(login, "button-authorize")
    login.wait_for_text("IN REVIEW")
    login.wait_for_element_absent('[data-cy="button-authorize"]')
    login.wait_for_element_visible('[data-cy="button-mark-as-released"]')
    login.wait_for_element_visible('[data-cy="button-reject"]')
    login.wait_for_element_visible('[data-cy="button-abort"]')

    # --- Mark as released → Accepted: both child plans mirror instruction status ---
    _confirm_workflow_button(login, "button-mark-as-released")
    login.wait_for_text("ACCEPTED")
    login.wait_for_element_visible('[data-cy="button-reconciliation-export"]')
    login.wait_for_element_visible('[data-cy="button-reconciliation-import"]')
    login.wait_for_element_absent('[data-cy="button-mark-as-released"]')
    login.assert_element_absent('[data-cy="button-close"]')
    login.wait_for_text("ACCEPTED", '[data-cy="plan-status-0"]')
    login.wait_for_text("ACCEPTED", '[data-cy="plan-status-1"]')
    login.wait_for_text("280.00", '[data-cy="summary-total-entitled"]')
    login.wait_for_text("0.00", '[data-cy="summary-total-delivered"]')

    # --- Export XLSX ---
    login.click('[data-cy="button-reconciliation-export"]')
    login.wait_for_text("Exporting XLSX started")
    login.open(detail_path)
    login.wait_for_element_visible('[data-cy="button-download-export"]')

    # --- Partial reconciliation: hh_a=140 (full), hh_b and hh_c left unreconciled ---
    instruction = FollowUpInstruction.objects.get(pk=instruction_id)
    partial_path = _build_xlsx_with_deliveries(
        instruction,
        [Decimal("140.00"), None, None],
    )
    _upload_reconciliation_xlsx(login, partial_path)

    login.open(detail_path)
    # hh_b and hh_c are left unreconciled, so neither child plan is fully reconciled
    # yet → both stay Accepted. Reconciling a payment to 0 would finalize it and lock
    # the plan against further reconciliation, so hh_c is deferred to the full step below.
    login.wait_for_text("ACCEPTED")
    login.wait_for_text("ACCEPTED", '[data-cy="plan-status-0"]')
    login.wait_for_text("ACCEPTED", '[data-cy="plan-status-1"]')
    # plan_one: delivered = hh_a(100); hh_b unreconciled; undelivered = 160 - 100 = 60
    login.wait_for_text("100.00", '[data-cy="plan-delivered-0"]')
    login.wait_for_text("60.00", '[data-cy="plan-undelivered-0"]')
    # plan_two: delivered = hh_a(40); hh_c unreconciled; undelivered = 120 - 40 = 80
    login.wait_for_text("40.00", '[data-cy="plan-delivered-1"]')
    login.wait_for_text("80.00", '[data-cy="plan-undelivered-1"]')
    # Instruction totals: delivered=140, undelivered=280-140=140
    login.wait_for_text("140.00", '[data-cy="summary-total-delivered"]')
    login.wait_for_text("140.00", '[data-cy="summary-total-undelivered"]')
    login.assert_element_absent('[data-cy="button-close"]')

    # --- Re-export after partial reconciliation ---
    login.click('[data-cy="button-reconciliation-export"]')
    login.wait_for_text("Exporting XLSX started")
    login.open(detail_path)
    login.wait_for_element_visible('[data-cy="button-download-export"]')

    # --- Full reconciliation: hh_a=140, hh_b=60 and hh_c=80 complete the remaining ---
    instruction.refresh_from_db()
    full_path = _build_xlsx_with_deliveries(
        instruction,
        [Decimal("140.00"), Decimal("60.00"), Decimal("80.00")],
    )
    _upload_reconciliation_xlsx(login, full_path)

    login.open(detail_path)
    # All payments fully delivered — instruction and both child plans transition to Finished
    login.wait_for_text("FINISHED")
    login.wait_for_text("FINISHED", '[data-cy="plan-status-0"]')
    login.wait_for_text("FINISHED", '[data-cy="plan-status-1"]')
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
    login.wait_for_text("CLOSED")
    login.assert_element_absent('[data-cy="button-close"]')
    login.assert_element_absent('[data-cy="button-reconciliation-export"]')
    login.assert_element_absent('[data-cy="button-reconciliation-import"]')
